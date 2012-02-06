#!/usr/bin/env ruby

require 'eventmachine'
require 'evma_httpserver'
require 'mongo'

module Romongo
	module Base
		def parse_qs(query_string)
			params = {}
			query_string.split("&").each do |one_qs|
				key, value = one_qs.split("=", 2)

				if(['ie', 'webkit', 'gecko', 'presto'].include? key)
					params['_core'] = key
				end
				if(['ieshell', 'se360', 'sogou', 'maxthon', 'chrome', 'safari', 'firefox', 'qqbrowser', 'opera', 'theworld'].include? key)
					params['_shell'] = key
					params['_shell'] = "#{key}#{value}" if 'ieshell' == key
				end
				params[key] = value if key
				# TODO: key with '.'
			end

			return params
		end
	end

	module Agent
		def post_init
			super

			@db = Mongo::Connection.new("10.3.18.197", 27017).db("ruby_ev_test")
			@cl = @db.collection("coll_table")
		end

		def process_http_request
			begin
				if @http_query_string
					bson = parse_qs(@http_query_string)
					@cl.insert(bson)
				else
				 	$stdout.print "#INFO#: #{@http_query_string.inspect} - #{bson.inspect}"
				end
			rescue
				 $stderr.print "#ERROR#: #{@http_query_string.inspect} - #{bson.inspect}"
			end
		end
	end
end

class RomongoAgent < EM::Connection
	include EM::HttpServer
	include Romongo::Base
	include Romongo::Agent

	def post_init
		super
		no_environment_strings
	end

	def process_http_request
		super

		response = EM::DelegatedHttpResponse.new(self)
		response.status = 204
		response.send_response
	end
end

EM.run{
	EM.start_server '0.0.0.0', 8080, RomongoAgent
}
