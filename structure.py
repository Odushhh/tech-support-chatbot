import os

def print_backend_structure():
    backend_dir = os.path.join(os.getcwd(), 'backend')
    for dirpath, dirnames, filenames in os.walk(backend_dir):
        # Calculate the level of depth
        depth = dirpath.replace(backend_dir, '').count(os.sep)
        indent = '|--' * depth
        
        # Print the directory name
        print(f"{indent} {os.path.basename(dirpath)}/")
        
        # Print the file names
        for filename in filenames:
            print(f"{indent}|-- {filename}")

if __name__ == "__main__":
    print_backend_structure()