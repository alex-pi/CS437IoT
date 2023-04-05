import boto3
from botocore.exceptions import ClientError
import json
import time
from common import *

class CertsHelper():
    def __init__(self, root_ca='AmazonRootCA1.pem'):
        # Create certs folder is not there.
        self.root_ca_path = os.path.join(CERTS_DIR, root_ca)
        try:
            os.makedirs(CERTS_DIR)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(CERTS_DIR):
                pass
            else: raise

    def get_cert_paths(self, thing_num):
        return (os.path.join(CERTS_DIR, cert_format.format(thing_num)),
                os.path.join(CERTS_DIR, pri_key_format.format(thing_num)))

    def get_cert_names(self, thing_num):
        return {
            'public_key': pub_key_format.format(thing_num),
            'private_key': pri_key_format.format(thing_num),
            'certificate_pem': cert_format.format(thing_num),
            'certificate_id': cert_id_format.format(thing_num)
        }

    def save_cert_file(self, file_name, content):
        file_path = os.path.join(CERTS_DIR, file_name)
        with open(file_path, 'w') as outfile:
            outfile.write(content)

        return file_path

    def delete_cert_files(self, thing_num):
        names = self.get_cert_names(thing_num)
        for _, name in names.items():
            try:
                os.remove(os.path.join(CERTS_DIR, name))
            except OSError:
                pass

    def read_cert_id(self, thing_num):
        file_path = os.path.join(CERTS_DIR, cert_id_format.format(thing_num))
        with open(file_path, 'r') as f:
            id_cert = f.read().replace('\n', '')

        trace(f'Cert Id from file: {id_cert}')
        return id_cert


class ThingsManager():

    def __init__(self, client=None):
        self.client = client if client else boto3.client('iot')
        self.ch = CertsHelper()

    def __call(self, operation, **args):
        try:
            resp = operation(**args)
        except ClientError as error:
            error(error.response)
            resp = error.response
        else:
            trace(json.dumps(resp, sort_keys=False, indent=2, default=str))

        return resp

    def create_thing(self, seq_num):
        resp = self.__call(self.client.create_thing, thingName = get_name(seq_num))
        self.__call(self.client.add_thing_to_thing_group,
                    thingGroupName = GROUP_NAME,
                    thingName = get_name(seq_num))
        return resp

    def delete_thing(self, seq_num):
        resp = self.__call(self.client.delete_thing, thingName = get_name(seq_num))
        return resp

    def delete_certificate(self, seq_num):
        thing_name = get_name(seq_num)
        cert_id = self.ch.read_cert_id(thing_num=seq_num)
        resp = self.__call(self.client.update_certificate,
                           certificateId = cert_id,
                           newStatus = 'INACTIVE')
        cert_details = self.__call(self.client.describe_certificate,
                                   certificateId = cert_id)
        certificate_arn = cert_details['certificateDescription']['certificateArn']
        self.__call(self.client.detach_thing_principal,
                    thingName = thing_name,
                    principal = certificate_arn)
        self.__call(self.client.detach_policy,
                    policyName = DEFAULT_POLICY,
                    target = certificate_arn)
        resp = self.__call(self.client.delete_certificate, certificateId = cert_id)

        if resp['ResponseMetadata']['HTTPStatusCode'] == 200:
            self.ch.delete_cert_files(thing_num=seq_num)
        return resp

    def attach_certificate(self, seq_num):
        thing_name = get_name(seq_num)
        resps = []
        resp = self.__call(self.client.create_keys_and_certificate, setAsActive = True)
        resps.append(resp)

        certificate_arn = resp['certificateArn']
        public_key = resp['keyPair']['PublicKey']
        private_key = resp['keyPair']['PrivateKey']
        certificate_pem = resp['certificatePem']
        certificate_id = resp['certificateId']

        file_names = self.ch.get_cert_names(seq_num)
        self.ch.save_cert_file(file_names['public_key'], public_key)
        self.ch.save_cert_file(file_names['private_key'], private_key)
        self.ch.save_cert_file(file_names['certificate_pem'], certificate_pem)
        self.ch.save_cert_file(file_names['certificate_id'], certificate_id)

        self.__call(self.client.attach_policy,
                    policyName = DEFAULT_POLICY,
                    target = certificate_arn)

        self.__call(self.client.attach_thing_principal,
                    thingName = thing_name,
                    principal = certificate_arn)

        return resps