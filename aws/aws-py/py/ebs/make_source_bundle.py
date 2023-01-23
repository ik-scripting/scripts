import os
import shutil
import tempfile

DOCKERRUN = 'Dockerrun.aws.json'
EXTENSIONS = '.ebextensions/'
ARCHIVE = 'zip'


def __create_version_file(environment, version_label, dockerrun_location, ebextensions_location):
    '''
    Create versioned application zip file
    '''
    temporary_directory = tempfile.mkdtemp()
    print temporary_directory
    try:
        deploy_dockerrun = os.path.join(temporary_directory, DOCKERRUN)
        print deploy_dockerrun
        deploy_extensions = os.path.join(temporary_directory, EXTENSIONS)
        shutil.copyfile(dockerrun_location, deploy_dockerrun)
        shutil.copytree(ebextensions_location, deploy_extensions)
        return shutil.make_archive("{}:{}".format(environment, version_label), ARCHIVE, root_dir=temporary_directory)
    finally:
        shutil.rmtree(temporary_directory)


def make_source_bundle(environment, version, dockerrun, ebextensions):
    bundled_zip_path = __create_version_file(environment=environment, version_label=version,
                                             dockerrun_location=dockerrun,
                                             ebextensions_location=ebextensions)
    return bundled_zip_path
