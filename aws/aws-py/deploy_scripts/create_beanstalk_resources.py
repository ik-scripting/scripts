#!/usr/bin/env python
'''
  Create/Update Elastic BeanStalk Environment.
  Support deploy different version of application and configuration.


  Usage example
  chmod +x make_environment.py
  ./create_beanstalk_resources.py --application "app-name" --deploymentrole "aws iam deployment role"
'''

import argparse

parser = argparse.ArgumentParser(description='Process Arguments.')
parser.add_argument('--application', type=str, required=True, dest='application')
parser.add_argument('--beanstalkservicerole', type=str, required=False, dest='beanstalk_service_role')
parser.add_argument('--appEnvironment', type=str, required=True, dest='app_environment')
parser.add_argument('--appversion', type=str, required=True, dest='version')
parser.add_argument('--overrideAppversion', type=str, required=True, dest='override_version')
parser.add_argument('--dockerrun', type=str, required=True, dest='dockerrun')
parser.add_argument('--ebextensions', type=str, required=True, dest='ebextensions')
parser.add_argument('--envConfFile', type=str, required=True, dest='config_file')
parser.add_argument('--profileConfFile', type=str, required=False, dest='profile_config_file', default=None)
parser.add_argument('--slnConfFile', type=str, required=True, dest='solution_conf_file')
parser.add_argument('--tagsFile', type=str, required=True, dest='tags_file')
parser.add_argument('--template', type=str, required=True, dest='template')

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from py.core.session import Session
    from py.core.config import Config
    from py.core.exports import Exports
    from py.ebs.ebcontext import EbContext
    from py.ebs.make_app_version import make_app_version
    from py.ebs.make_application import make_application
    from py.ebs.make_config_template_version import make_config_version
    from py.ebs.make_environment import make_environment
    from py.ebs.make_source_bundle import make_source_bundle

    args = parser.parse_args()
    session = Session.factory()
    config = Config(Exports(session))

    args = parser.parse_args()

    eb_context = EbContext.factory(application=args.application,
                                   beanstalk_service_role=args.beanstalk_service_role,
                                   version=args.version,
                                   override_version=args.override_version,
                                   session=session)

    make_application(eb_context=eb_context)

    bundle_zip_path = make_source_bundle(environment=args.app_environment,
                                         version=args.version,
                                         dockerrun=args.dockerrun,
                                         ebextensions=args.ebextensions)

    make_app_version(bundle_zip_path=bundle_zip_path,
                     eb_context=eb_context)

    env_options = config.load_environment_config(env_conf_file=args.config_file,
                                          profile_config_file=args.profile_config_file)

    make_config_version(environment=args.app_environment,
                        env_options=env_options,
                        solution_conf_file=args.solution_conf_file,
                        eb_context=eb_context)

    make_environment(environment=args.app_environment,
                     template=args.template,
                     eb_context=eb_context,
                     tags_file=args.tags_file)
