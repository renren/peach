
SETUP
===============
> bundle install

RUN
===============
> bundle exec ruby romongo.rb

DOCUMENTS
===============
event machine
---------------
the http request details are available via the following instance variables:
#   @http_protocol
#   @http_request_method
#   @http_cookie
#   @http_if_none_match
#   @http_content_type
#   @http_path_info
#   @http_request_uri
#   @http_query_string
#   @http_post_content
#   @http_headers

RomongoTask
--------------

$reduce task for browsers stat
<pre>
use beacon_sys

db.runCommand({"group" : {
	"ns" : "user_browser_logs",
	"key" : "_core",
	"initial" : {"brs" : {}},
	"$reduce" : function(doc, prev) {
		if ( doc._core in prev.brs ) {
			if ( doc._shell in prev.brs[doc._core] ) {
				prev.brs[doc._core][doc._shell]++;
			} else {
				prev.brs[doc._core][doc._shell] = 1;
			}
		} else {
			prev.brs[doc._core] = {}
		}
	},
	"$finalize" : function(prev) {
		for (i in prev.brs) {;}
	}
}})
</pre>

