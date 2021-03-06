# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script is used to synthesize generated parts of this library."""

import synthtool as s
import synthtool.gcp as gcp
import logging
import re

logging.basicConfig(level=logging.DEBUG)

gapic = gcp.GAPICGenerator()

v2_library = gapic.ruby_library(
    'logging', 'v2',
    config_path='/google/logging/artman_logging.yaml',
    artman_output_name='google-cloud-ruby/google-cloud-logging'
)
s.copy(v2_library / 'lib/google/cloud/logging/v2')
s.copy(v2_library / 'lib/google/logging/v2')

# Omitting lib/google/cloud/logging/v2.rb for now because we are not exposing
# the low-level API.

# PERMANENT: Handwritten layer owns Logging.new so low-level clients need to
# use Logging::V2.new instead of Logging.new(version: :v2). Update the
# examples and tests.
s.replace(
    [
      'lib/google/cloud/logging/v2/config_service_v2_client.rb',
      'lib/google/cloud/logging/v2/logging_service_v2_client.rb',
      'lib/google/cloud/logging/v2/metrics_service_v2_client.rb'
    ],
    'require "google/cloud/logging"',
    'require "google/cloud/logging/v2"')
s.replace(
    'lib/google/cloud/logging/v2/config_service_v2_client.rb',
    'Google::Cloud::Logging::Config\\.new\\(version: :v2\\)',
    'Google::Cloud::Logging::V2::ConfigServiceV2Client.new')
s.replace(
    'lib/google/cloud/logging/v2/logging_service_v2_client.rb',
    'Google::Cloud::Logging::Logging\\.new\\(version: :v2\\)',
    'Google::Cloud::Logging::V2::LoggingServiceV2Client.new')
s.replace(
    'lib/google/cloud/logging/v2/metrics_service_v2_client.rb',
    'Google::Cloud::Logging::Metrics\\.new\\(version: :v2\\)',
    'Google::Cloud::Logging::V2::MetricsServiceV2Client.new')

# Support for service_address
s.replace(
    'lib/google/cloud/logging/v*/*_client.rb',
    '\n(\\s+)#(\\s+)@param exception_transformer',
    '\n\\1#\\2@param service_address [String]\n' +
        '\\1#\\2  Override for the service hostname, or `nil` to leave as the default.\n' +
        '\\1#\\2@param service_port [Integer]\n' +
        '\\1#\\2  Override for the service port, or `nil` to leave as the default.\n' +
        '\\1#\\2@param exception_transformer'
)
s.replace(
    'lib/google/cloud/logging/v*/*_client.rb',
    '\n(\\s+)metadata: nil,\n\\s+exception_transformer: nil,\n',
    '\n\\1metadata: nil,\n\\1service_address: nil,\n\\1service_port: nil,\n\\1exception_transformer: nil,\n'
)
s.replace(
    'lib/google/cloud/logging/v*/*_client.rb',
    'service_path = self\\.class::SERVICE_ADDRESS',
    'service_path = service_address || self.class::SERVICE_ADDRESS'
)
s.replace(
    'lib/google/cloud/logging/v*/*_client.rb',
    'port = self\\.class::DEFAULT_SERVICE_PORT',
    'port = service_port || self.class::DEFAULT_SERVICE_PORT'
)

# https://github.com/googleapis/gapic-generator/issues/2124
s.replace(
    'lib/google/cloud/logging/v2/credentials.rb',
    'SCOPE = \[[^\]]+\]\.freeze',
    'SCOPE = ["https://www.googleapis.com/auth/logging.admin"].freeze')

# https://github.com/googleapis/gapic-generator/issues/2242
def escape_braces(match):
    expr = re.compile('^([^`]*(`[^`]*`[^`]*)*)([^`#\\$\\\\])\\{([\\w,]+)\\}')
    content = match.group(0)
    while True:
        content, count = expr.subn('\\1\\3\\\\\\\\{\\4}', content)
        if count == 0:
            return content
s.replace(
    'lib/google/cloud/logging/v2/**/*.rb',
    '\n(\\s+)#[^\n]*[^\n#\\$\\\\]\\{[\\w,]+\\}',
    escape_braces)

# https://github.com/googleapis/gapic-generator/issues/2243
s.replace(
    'lib/google/cloud/logging/v2/*_client.rb',
    '(\n\\s+class \\w+Client\n)(\\s+)(attr_reader :\\w+_stub)',
    '\\1\\2# @private\n\\2\\3')

# https://github.com/googleapis/gapic-generator/issues/2279
s.replace(
    'lib/**/*.rb',
    '\\A(((#[^\n]*)?\n)*# (Copyright \\d+|Generated by the protocol buffer compiler)[^\n]+\n(#[^\n]*\n)*\n)([^\n])',
    '\\1\n\\6')

# https://github.com/googleapis/google-cloud-ruby/issues/3058
s.replace(
    'lib/google/cloud/logging/v2/*_client.rb',
    '(require \".*credentials\"\n)\n',
    '\\1require "google/cloud/logging/version"\n\n'
)
s.replace(
    'lib/google/cloud/logging/v2/*_client.rb',
    'Gem.loaded_specs\[.*\]\.version\.version',
    'Google::Cloud::Logging::VERSION'
)

s.replace(
    [
        'lib/google/cloud/logging/v2/config_service_v2_client.rb',
        'lib/google/cloud/logging/v2/doc/google/logging/v2/logging_config.rb'
    ],
    '\{Google::Logging::V2::ConfigServiceV2::CreateSink sinks::create\}',
    '{Google::Logging::V2::ConfigServiceV2#create_sink}'
)
s.replace(
    [
        'lib/google/cloud/logging/v2/config_service_v2_client.rb',
        'lib/google/cloud/logging/v2/doc/google/logging/v2/logging_config.rb'
    ],
    '\{Google::Logging::V2::ConfigServiceV2::UpdateSink sinks::update\}',
    '{Google::Logging::V2::ConfigServiceV2#update_sink}'
)
