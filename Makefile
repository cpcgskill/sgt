.PHONY: build_image publish_image pull_image rm_image stop_container rm_container run_container

repository_name = hkccr.ccs.tencentyun.com/cp-pr/
image_name = self_growth_toolchain
image_version = 0.2.5
this_version_image_name = ${repository_name}${image_name}:${image_version}
container_name = self_growth_toolchain
mongodb_database_url = mongodb://admin:xC5GP5aQdmrgLo7FOicc@10.0.8.3:9586/sgtone?authSource=admin
sgtone_key = 'pCghSlDywE5THHAfhfoz'

build_image:
	pip freeze > requirements.txt
	docker build -t ${this_version_image_name} .

publish_image: build_image
	docker push ${this_version_image_name}

pull_image:
	docker pull ${this_version_image_name}

rm_image:
	docker image rm `docker image ls -q -f "reference=$(repository_name)$(image_name):*"`

stop_container:
	docker stop ${container_name}

rm_container: stop_container
	docker rm ${container_name}
	#docker image prune -f

run_container: pull_image
	docker run -d -p 10011:8000 -e mongodb_database_url=${mongodb_database_url} -e sgtone_key=${sgtone_key} --name=${container_name} --restart=always ${this_version_image_name}
