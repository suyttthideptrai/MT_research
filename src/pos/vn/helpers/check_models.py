import os
# path: src/pos/vn/helpers

def check_models(file_path, dir_path):
    # Check if the file exists
    file_exists = os.path.isfile(file_path)
    
    # Check if the directory exists
    dir_exists = os.path.isdir(dir_path)
    
    # Display the result
    if file_exists and dir_exists:
        print(f"Both the file '{file_path}' and the directory '{dir_path}' exist.")
        return True
    elif not file_exists and not dir_exists:
        print(f"Neither the file '{file_path}' nor the directory '{dir_path}' exist.")
        return False
    elif not file_exists:
        print(f"The file '{file_path}' does not exist, but the directory '{dir_path}' exists.")
        return False
    elif not dir_exists:
        print(f"The file '{file_path}' exists, but the directory '{dir_path}' does not exist.")
        return False


