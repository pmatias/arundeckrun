########
# Copyright (c) 2016 Antillion Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

import sys
import os

import unittest
import importlib

from mock import Mock, MagicMock, PropertyMock
from mock import patch

sys.path.append(os.getcwd() + '/rundeck')

from IPython import embed
from client import Rundeck
import responses
from yattag import Doc

from urlparse import urlsplit, parse_qs as parse_querystring


class TestRundeckApi(unittest.TestCase):
  def rundeck_success(self, body, api_version=14):
    return '<result success="true" apiversion="{0}">{1}</result>'.format(api_version, body)

  def build_url(self, path):
    return 'http://rundeck.host/api/11/{0}'.format(path)

  def build_project_url(self, project_name, path):
    return self.build_url('project/{0}/{1}'.format(project_name, path))

  @responses.activate
  def test_list_projects(self):
    project_description = 'the description'
    project_url = 'the url'
    project_name = 'the name'
    responses.add(responses.GET,
                  self.build_url('projects'),
                  body=self.rundeck_success('<projects count="1">'
                                            + '<project><name>{0}</name>'.format(project_name)
                                            + '<description>{0}</description>'.format(
                    project_description)
                                            + '<url>{0}</url></project>'.format(project_url)
                                            + '</projects>'),
                  content_type='text/xml', status=200)

    projects = self.rundeck_api.list_projects()

    self.assertEquals(len(projects), 1)

    self.assertEquals(projects[0]['name'], project_name)
    self.assertEquals(projects[0]['description'], project_description)
    self.assertEquals(projects[0]['url'], project_url)

  @responses.activate
  def test_list_jobs(self):
    project_name = 'test_project'
    jobs = [
      {'name': 'job 1', 'id': '1', 'project': project_name, 'description': 'job 1 description'}]

    doc, tag, text = Doc().tagtext()

    with tag('jobs', count=len(jobs)):
      for job in jobs:
        with tag('job'):
          with tag('name'):
            text(job['name'])
          with tag('project'):
            text(job['project'])
          with tag('description'):
            text(job['description'])

    responses.add(responses.GET,
                  'http://rundeck.host/api/11/jobs?project=test_project',
                  match_querystring=True,
                  body=self.rundeck_success(doc.getvalue()),
                  content_type='text/xml', status=200)

    project_jobs = self.rundeck_api.list_jobs(project_name)

    self.assertEquals(len(project_jobs), len(jobs))
    self.assertEquals(project_jobs[0]['name'], jobs[0]['name'])


  @responses.activate
  def test_import_project_archive(self):
    project_name = 'test_project'
    path_url = self.build_project_url(project_name, 'import')

    responses.add(responses.PUT,
                  path_url,
                  body=self.rundeck_success('<import status="successful"></import>'),
                  content_type='text/xml', status=200)

    with open('rundeck/tests/test-file.zip', 'rb') as project_archive:
      archive_data = project_archive.read()
      import_result = self.rundeck_api.import_project_archive(project_name, archive_data,
                                                              jobUuidOption='preserve',
                                                              importExecutions=False,
                                                              importConfig=False,
                                                              importACL=False)

    import_call = responses.calls[0]
    params = parse_querystring(urlsplit(responses.calls[0].request.path_url).query)

    self.assertEquals(import_call.request.body, archive_data)
    self.assertEquals(import_call.request.headers['Content-Type'], 'application/zip')

    self.assertEquals(params['jobUuidOption'], ['preserve'])
    self.assertEquals(params['importExecutions'], ['False'])
    self.assertEquals(params['importConfig'], ['False'])
    self.assertEquals(params['importACL'], ['False'])

    self.assertEquals(import_result['succeeded'], True)

  @responses.activate
  def test_import_job(self):
    responses.add(responses.POST, self.build_url('jobs/import'),
                  body=self.rundeck_success(
                    '<succeeded count="1"><job index="1"><id>some-id</id></job></succeeded>'),
                  content_type='text/xml', status=200)
    job_definition = '<job><definition/></job>'
    import_result = self.rundeck_api.import_job(job_definition, fmt='xml', dupeOption='update',
                                                project='test_project', uuidOption='preserve')

    params = parse_querystring(responses.calls[0].request.body)
    self.assertEquals(params['format'][0], 'xml')
    self.assertEquals(params['dupeOption'][0], 'update')
    self.assertEquals(params['project'][0], 'test_project')
    self.assertEquals(params['uuidOption'][0], 'preserve')
    self.assertEquals(params['xmlBatch'][0], job_definition)

    self.assertEquals(import_result['failed'], None)
    self.assertEquals(import_result['skipped'], None)

    self.assertEquals(len(import_result['succeeded']), 1)

    self.assertEquals(import_result['succeeded'][0]['id'], 'some-id')

  def setUp(self):
    self.rundeck_api = Rundeck(server='rundeck.host', api_token='some-api-token', port=80,
                               protocol='http')
