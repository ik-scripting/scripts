# -*- coding: utf-8 -*-

import subprocess
result = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE)
result.stdout.decode('utf-8')

env="prod"
team="supplychain"


class tfmwrapper:
    """terraform wrapper class"""
    @staticmethod
    def extract_what_to_import():
        cmd="terragrunt plan -no-color"
        working_dir=f"~/infrastructure/s3-bucket/environments/{env}/eu-west-1/{team}" #add correct dir here
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, cwd=working_dir)
        output=result.stdout.decode('utf-8').split("\n")
        filename=f"{env}_{team}"
        #f = open(f"{env}_{team}.sh", "w")
        f = open(f"{filename}.sh", "w")
        f.write("#!/bin/bash\n")
        #f.write(f"# aws-vault exec hbi-{team} -- ./{env}_{team}.sh\n")
        f.write(f"# aws-vault exec hbi-{env} -- ./{filename}.sh\n")
        for el in output:
            if "aws_s3_bucket_policy.bucket" in el and "will be created" in el:
                address=el.split()[1].strip()
                id=address.replace("aws_s3_bucket_policy.bucket[\"","").replace("\"]","").strip()
                #print(address,id)
                cmd=f"terragrunt import '{address}' {id}\n"
                f.write(cmd)
        f.close()