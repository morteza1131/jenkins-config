# Jenkins Job Configuration

You can:

- Get all jenkins jobs xml configuration
- List all jenkins jobs
- Change scripted pipeline to GitSCM pipeline
- Store jenkins scripted pipeline script on disk and then use it as jenkins file for GitSCM pipeline config
- Backeup jenkins jobs xml configuration

```bash
usage: jenkins_config.py [-h] --pass JENKINS_PASS [--server JENKINS_URL] [--user JENKINS_USER] [--list]
                         [--get scripts|configs|JOB_NAME] [--restore JOB_NAME|all] [--set JOB_NAME|all] [--git-url URL]

optional arguments:
  -h, --help            show this help message and exit
  --pass JENKINS_PASS   Jenkins Password!
  --server JENKINS_URL  Jenkins URL(defualt: http://jenkins.example.com)
  --user JENKINS_USER   Jenkins Username(defualt: root)
  --list                List all jenkins jobs!
  --get scripts|configs|JOB_NAME
                        Print complete xml config of a job or store xml config or script section of all jobs on disk,
                        configs are store in "./job_configs/" and scripts are store in "./"
  --restore JOB_NAME|all
                        Restore config of job(s) from "./job_configs/JOB_NAME.xml"
  --set JOB_NAME|all    Replace script config to git for job(s), --git-url requaired,example: set JOB_NAME"
  --git-url URL         Url of git project to set for jenkins files"
  ```
