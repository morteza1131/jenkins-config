#!/bin/python3
##Execute this script with -h to see its options, ./jenkins_config.py --help

from os import name
from typing import Text
import xml.etree.ElementTree as ET
import jenkins
import argparse
import sys

## Help menu:
parser=argparse.ArgumentParser()
parser.add_argument('--pass',metavar='JENKINS_PASS',required=True, help='Jenkins Password!')
parser.add_argument('--server',metavar='JENKINS_URL',required=True, help='Jenkins URL(http://jenkins.example.com)')
parser.add_argument('--user',metavar='JENKINS_USER', default='root', help='Jenkins Username(defualt: root)')
parser.add_argument('--list',action='store_true', help='List all jenkins jobs!')
parser.add_argument('--get',metavar='scripts|configs|JOB_NAME',help='Print complete xml config of a job or store xml config or script section of all jobs on disk, configs are store in "./job_configs/" and scripts are store in "./"')
parser.add_argument('--restore',metavar='JOB_NAME|all',help='Restore config of job(s) from "./job_configs/JOB_NAME.xml"')
parser.add_argument('--set',metavar='JOB_NAME|all',help='Replace script config to git for job(s), --git-url, --git-cred-name and --git-branch are requaired,example: set JOB_NAME')
parser.add_argument('--git-url',metavar='URL',help='Url of git project to set for jenkins files')
parser.add_argument('--git-cred-name',metavar='CRED_NAME',default='git_cred',help='Name of Jenkins credential created before for connection to git')
parser.add_argument('--git-branch',metavar='BRANCH_NAME',default='master',help='Git branch for GitSCM Jenkinsfile')
args=parser.parse_args()
args_vars=vars(parser.parse_args())

if not args.get and not args.set and not args.list:
  print("Use an argument: --list|--get|--set")
  sys.exit()

if args.set and not args.git_url:
  print("To set git repo for script(s) you need to pass --git-url git@git.example.com:example/example.git")
  sys.exit()
elif args.set and args.git_url:
  git_url=args_vars['git_url']
  git_cred_name=args_vars['git_cred_name']
  git_branch=args_vars['git_branch']
  scm_config_temp ="""
    <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.53">
      <scm class="hudson.plugins.git.GitSCM" plugin="git@3.9.0">
        <configVersion>2</configVersion>
        <userRemoteConfigs>
          <hudson.plugins.git.UserRemoteConfig>
            <url>"""+git_url+"""</url>
            <credentialsId>"""+git_cred_name+"""</credentialsId>
          </hudson.plugins.git.UserRemoteConfig>
        </userRemoteConfigs>
        <branches>
          <hudson.plugins.git.BranchSpec>
            <name>"""+git_branch+"""</name>
          </hudson.plugins.git.BranchSpec>
        </branches>
        <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
        <submoduleCfg class="list"/>
        <extensions/>
      </scm>
      <scriptPath>morteza</scriptPath>
      <lightweight>true</lightweight>
    </definition>"""

## Functions:
username=args_vars['user']
server = jenkins.Jenkins(args_vars['server'],username , password=args_vars['pass'])
try:
  jobs = server.get_jobs()
except Exception as e:
  print(str(e))
  sys.exit()

def get_config(action):
  for job in jobs:
      job_name= job.get('name')
      config = server.get_job_config(job_name)
      root = ET.fromstring(config)
      xml_str = ET.tostring(root, encoding='unicode', method='xml')
      if action == 'configs':
        try:
          f = open("./job_configs/" + job_name + ".xml", "w")
          f.write(xml_str)
          f.close()
          print('Config for job "' + job_name +'" stored in' + "./job_configs/" + job_name + ".xml")
        except:
          print("Please create './job_configs' directory")
          break
      elif action == 'scripts':
        counter1 = 0
        counter2 = 0
        for child in root:
            if child.tag == "definition":
                while True:
                    try:
                        if root[counter1][counter2].tag == 'script':
                            script = root[counter1][counter2].text
                            f = open(job_name, "w")
                            f.write(script)
                            f.close()
                            print('script for job "' + job_name +'" stored in' + "./" + job_name)
                            break
                        counter2 += 1
                    except Exception as e:
                        print('Could not found Script for job "' + job_name +'", error: ' + str(e))
                        break
                break
            counter1 += 1
      elif action == job_name:
        print(xml_str)
        break
        
def list_jobs():
  counter = 0
  for job in jobs:
    counter+=1
    print(str(counter)+": "+ job.get('name'))

def set(job_name):
  config = server.get_job_config(job_name)
  root = ET.fromstring(config)
  counter = 0
  for child in root:
    counter += 1
    if child.tag == 'definition':
      root.remove(root[counter])
      break
  test = ET.fromstring(scm_config_temp)
  test.find("scriptPath").text = job_name
  root.insert(counter,test)
  xml_str = ET.tostring(root, encoding='unicode', method='xml')
  server.reconfig_job(job_name,xml_str)
  print('Job ' + job_name + ' reconfigured!')
  print("Git url: "+ giturl)
def set_config(job_name):
  if job_name == 'all':
    for job in jobs:
      try:
        job_name= job.get('name')
        set(job_name)
      except Exception as e:
        print('Could not config already configured job "' + job_name +'"!, error: ' + str(e))
  else:
    set(job_name)

def restore(job_name):
  f = open("./job_configs/" + job_name + ".xml", "r")
  tree = ET.parse(f)
  root = tree.getroot()
  xml_str = ET.tostring(root, encoding='unicode', method='xml')
  server.reconfig_job(job_name,xml_str)
  print('Job ' + job_name + ' Restored!')
  f.close()
  
def restore_config(job_name):
  if job_name == 'all':
    for job in jobs:
      try:
        job_name= job.get('name')
        restore(job_name)
      except Exception as e:
        print('Could not restore job "' + job_name +'"!, error: ' + str(e))
  else:
    restore(job_name)

if args.get:
  action = args_vars['get']
  get_config(action)

if args.list:
  list_jobs()

if args.set:
  job_name = args_vars['set']
  set_config(job_name)

if args.restore:
  job_name = args_vars['restore']
  set_config(job_name)