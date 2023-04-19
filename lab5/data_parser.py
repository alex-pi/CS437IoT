import re

# pattern to match each log entry
pattern = re.compile(r'-- Timestamp: ([0-9]+\.[0-9]+)\s+'
                     r'"location": \[(-?\d+\.\d+),(-?\d+\.\d+)\]\s+'
                     r'"oxygen_saturation": ([0-9\.]+), "heart_rate": (\d+)\s*'
                     r'(?:\"temperature\": ([0-9\.]+))?\s*'
                     r'(?:\"air_quality\": ([0-9\.]+))?')

with open("simulation_2023_4_13_10_52_55_READABLE.txt", "r") as f:
    animals_data = f.read()

animals_logs = animals_data.split("=============== ")

with open("simulation_data.csv", "w") as output:
    output.write('animal_id,animal,timestamp,lat,lon,oxygen_sat,heart_rate,temperature,air_quality\n')
    for animal_log in animals_logs[1:]:
        animal_log_line0 = animal_log.strip().split("\n\n")[0]

        animal, animal_id = animal_log_line0.split()[0].split(':')
        print(f"{animal}ID: {animal_id}")

        # Search for matches in the log text
        for match in re.finditer(pattern, animal_log):
            # Extract the data from the match
            timestamp = float(match.group(1))
            lat = float(match.group(2))
            lon = float(match.group(3))
            oxygen_sat = float(match.group(4)) if match.group(4) is not None else None
            heart_rate = int(match.group(5)) if match.group(5) is not None else None
            temperature = float(match.group(6)) if match.group(6) is not None else None
            air_quality = float(match.group(7)) if match.group(7) is not None else None

            # Write a row in the output file
            row = f'{animal_id},{animal},{timestamp},{lat},{lon},{oxygen_sat},{heart_rate},{temperature},{air_quality}\n'
            output.write(row)
