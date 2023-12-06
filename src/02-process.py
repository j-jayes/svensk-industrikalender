import os

def remove_br_tags(directory_path):
    """
    Removes all <br/> tags from the files in the specified directory.

    Args:
        directory_path (str): The path to the directory containing the files.

    Returns:
        None
    """
    # List all files in the directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    for file_name in files:
        try:
            with open(os.path.join(directory_path, file_name), 'r', encoding='utf-8') as file:
                content = file.read()
                # Replace <br/> tags with empty string
                modified_content = content.replace('<br/>', '')

            with open(os.path.join(directory_path, file_name), 'w', encoding='utf-8') as file:
                file.write(modified_content)
        except UnicodeDecodeError as e:
            print(f"Error decoding file: {file_name}. {str(e)}")

# Call the function
remove_br_tags("data/raw/svindkal")