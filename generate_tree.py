import os


def generate_tree(directory, level=3, indent=""):
    if level < 0:
        return
    for root, dirs, files in os.walk(directory):
        level -= 1
        print(indent + os.path.basename(root) + "/")
        indent += "    "
        for file in files:
            print(indent + file)
        for dir in dirs:
            generate_tree(os.path.join(root, dir), level, indent)
        break


if __name__ == "__main__":
    project_root = "C:\\Users\\35196\\password\\exams"
    generate_tree(project_root)
