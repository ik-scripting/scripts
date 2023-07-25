# An implicit guard target, used by other targets to ensure
# that environment variables are set before beginning tasks
assert-%:
	@ if [ "${${*}}" = "" ]; then \
	    echo "Environment variable $* not set"; \
	    exit 1; \
	fi

apply: assert-TF_VAR_aws_profile require-tf require-ansible ansible-roles
	@ if [ -z "$TF_VAR_pub_key" ]; then \
		echo "\$TF_VAR_pub_key is empty; run 'make keypair' first!"; \
		exit 1; \
	fi
	terraform apply
  
