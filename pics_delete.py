import os

# List of file paths to delete
files_to_delete = ['webpage_screenshot_1.png', 'webpage_screenshot_2.png', 'webpage_screenshot_3.png','webpage_screenshot_4.png', 'neg_webpage_screenshot_1.png','neg_webpage_screenshot_2.png','neg_webpage_screenshot_3.png','neg_webpage_screenshot_4.png','neg_webpage_screenshot_5.png']

# Delete each file
for file_path in files_to_delete:
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except PermissionError:
        print(f"Permission denied: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
