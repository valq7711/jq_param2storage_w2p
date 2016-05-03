## jq_param2storage_w2p
As of jQuery 1.8, the `$.param()` method no longer uses `jQuery.ajaxSettings.traditional` as its default setting and will default to false.
So, `$.param()` returns string that is structured like:
<pre><code>        cmd=get-records
        &limit= 50
        &offset= 0
        &selected[]= 1
        &selected[]= 2
        &searchLogic= AND
        &search[0][field]= fname
        &search[0][type]= text
        &search[0][operator]= is
        &search[0][value]= %D0%92%D0%B0%D0%BB%D0%B5%D1%80%D0%B8%D0%B9
        &search[1][field]= age
        &search[1][type]= int
        &search[1][operator]= between
        &search[1][value][]= 10
        &search[1][value][]= 0.333
        &sort[0][field]= fname
        &sort[0][direction]= asc
        &sort[1][field]= lname
        &sort[1][direction]= desc
</code></pre>
Module contains only one function `jq_param_w2p(str_or_buffer, rewind = True)` that converts JQuery-param-string to web2py `Storage` object or `dict`
(if it's used outside of web2py and couldn't import Storage)<br>
It could be used to interact with [W2UI JavaScript UI Library](http://w2ui.com/web/home) 
