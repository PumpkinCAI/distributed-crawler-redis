from publisher import Publisher
import os
if __name__ == '__main__':
    package_path = os.getcwd()
    project_name = os.path.basename(package_path) 
    Publisher().stop(project_name)


