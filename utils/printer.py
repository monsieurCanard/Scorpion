def print_metadata(filename, extension, metadata):
    print("\n================================")
    print(f"Extractor Metadata from {extension} file -> {filename}")
    print("================================")
    for key, value in metadata.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict):
                    print(f"  {sub_key}:")
                    for sub_sub_key, sub_sub_value in sub_value.items():
                        print(f"    {sub_sub_key}: {sub_sub_value}")
                else:
                    print(f"  {sub_key}: {sub_value}")
        elif isinstance(value, list):
            print(f"{key}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{key}: {value}")

    print("\n")
