#!/usr/bin/env ruby

require 'eventmachine'
require 'evma_httpserver'
require 'mongo'
require 'yaml'


module Romongo
	# Constants
	CONFIG = YAML.load_file(File.expand_path("./config.yml", File.dirname(__FILE__)))

	BR_CORE_KEY  = CONFIG['browser']['core']['key']
	BR_CORE_VER_KEY  = CONFIG['browser']['core']['ver_key']
	BR_CORE_MEMBERS  = CONFIG['browser']['core']['members']
	BR_SHELL_KEY = CONFIG['browser']['shell']['key']
	BR_SHELL_VER_KEY = CONFIG['browser']['shell']['ver_key']
	BR_SHELL_MEMBERS = CONFIG['browser']['shell']['members']

	MONGO_HOST =  CONFIG['mongo']['host']
	MONGO_PORT =  CONFIG['mongo']['port']
	MONGO_DB =  CONFIG['mongo']['db']
	MONGO_COLLECTION =  CONFIG['mongo']['collection']

	# Basic functions
	module Base
		def parse_qs(query_string)
			params = {}
			query_string.split("&").each do |one_qs|
				key, value = one_qs.split("=", 2)

				if(BR_CORE_MEMBERS.include? key)
					params[BR_CORE_KEY] = key
					params[BR_CORE_VER_KEY] = value
				end
				if(BR_SHELL_MEMBERS.include? key)
					params[BR_SHELL_KEY] = key
					params[BR_SHELL_VER_KEY] = value
				end
				if 'ieshell' == key and !params[BR_SHELL_KEY]
					params[BR_SHELL_KEY] = key
					params[BR_SHELL_VER_KEY] = value
				end
				params[key] = value if key
				# TODO: key with '.'
			end
			params['time'] = Time.now

			return params
		end
	end

	# Agent actions
	module Agent
		def post_init
			super

			@db = Mongo::Connection.new(MONGO_HOST, MONGO_PORT, :pool_size => 50, :pool_timeout => 5).db(MONGO_DB)
			@cl = @db.collection(MONGO_COLLECTION)
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


if __FILE__ == $0

	cf = YAML.load_file(File.expand_path("./config.yml", File.dirname(__FILE__)))
	host = cf['romongo']['agent']['host']
	port = cf['romongo']['agent']['port']

	EM.run{
		EM.start_server host, port, RomongoAgent
	}

end
