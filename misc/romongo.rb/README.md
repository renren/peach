
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

db.user_browser_logs.group({
	"ns" : "user_browser_logs",
	"key" : "_core",
	"initial" : {"brstat" : {"core" : {}, "vender" : {}}},
	"$reduce" : function(doc, prev) {
		if ( doc._core in prev.brstat.core ) {
			if ( doc._shell in prev.brstat.core[doc._core] ) {
				prev.brstat.core[doc._core][doc._shell]++;
			} else {
				prev.brstat.core[doc._core][doc._shell] = 1;
			}
		} else {
			prev.brstat.core[doc._core] = {};
			prev.brstat.core[doc._core][doc._shell] = 1;
		}
		if ( doc._shell in prev.brstat.vender ) {
			if ( doc._shell_ver in prev.brstat.vender[doc._shell] ) {
				prev.brstat.vender[doc._shell][doc._shell_ver]++;
			} else {
				prev.brstat.vender[doc._shell][doc._shell_ver] = 1;
			}
		} else {
			prev.brstat.vender[doc._shell] = {};
			prev.brstat.vender[doc._shell][doc._shell_ver] = 1;
		}
	},
	"$finalize" : function(prev) {
		for (i in prev.brstat) {;}
	}
})
</pre>

