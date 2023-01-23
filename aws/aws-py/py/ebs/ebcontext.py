class EbContext(object):
    def __init__(self, application, session, beanstalk_service_role=None, version=None, override_version=None):
        self.application = application
        self.beanstalk_service_role = beanstalk_service_role
        self.version = version
        self.override_version = override_version
        self.eb_client = session.current.client('elasticbeanstalk')
        self.s3_resource = session.current.resource('s3')

    @staticmethod
    def factory(application, session, beanstalk_service_role=None, version=None, override_version=None):
        return EbContext(application=application,
                         session=session,
                         beanstalk_service_role=beanstalk_service_role,
                         version=version,
                         override_version=override_version
                        )

    def __str__(self):
        return self.__dict__
