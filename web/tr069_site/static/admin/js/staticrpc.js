var AJAX_LOCK         = false;     // 锁定是否正在进行ajax请求
var AJAXLOCK_TIMEOUOT = 1000*530;  // django跟acs的超时时间设置为530s是因为acs跟用户的超时时间为520
var SET_FALG_HREF     = false;     // 设置是否更改href的属性
var CURRENT_RPC       = "";

/*
 *函数功能：获取url地址
 *参数：
 *  rpc_name：要执行的rpc名字
 *返回值：
 *  url：组建好的url地址
*/
function getURL(rpc_name){
    var pathname = window.location.pathname
    var revert = pathname.split('/')[4]
    var worklist_id = pathname.split('/')[5]
    var url = "/itms/" + this.cpe_id +"/ajax_static_rpc_request/"+rpc_name+"/"+revert+"/"+worklist_id+"/";
    return url
}

/*
 *函数功能：获取指定form中的所有的<input>和<select>对象  
 *参数：
 *  form_id：表单id值
 *返回值：
 *  elements：<input>和<select>对象对象列表
*/
function getElements(form_id) {
 
    var form = document.getElementById(form_id);    
    var elements = new Array();    
    var tagInput = form.getElementsByTagName('input');
    var tagSelect = form.getElementsByTagName('select');

    for (var j = 0; j < tagInput.length; j++){  
         elements.push(tagInput[j]);  
    }
    
    for (var j = 0; j < tagSelect.length; j++){  
         elements.push(tagSelect[j]);  
    }  
    return elements;    
}

/*
 *函数功能：获取表单数据
 *参数：无
 *返回值：
 *  dict_args：json数据格式{参数名：参数值}
*/
function getFormValue(){
    var elements = getElements("form_id")
    var dict_args = {};
    
    for (i in elements){
        var element = elements[i];
        var element_type = element.type.toLowerCase();
        
        switch (element_type){
            case 'select-one':
                dict_args[element.name] = element.value;
                break;
            case 'text':    
                dict_args[element.name] = element.value;
                break;
            case 'checkbox':    
            case 'radio':    
                if (element.checked)    
                    dict_args[element.name] = element.value;
        }
    }
    return dict_args;    
}

/*
 *函数功能：给所有的超级链接添加是否执行的方法
 *参数：无
 *返回值：无
*/
function setHref(){
    var a_elements = document.getElementsByTagName('a');
    for (i in a_elements){
        var element = a_elements[i];
        element.onclick = function checkLock(){
                                                if (AJAX_LOCK){
                                                    alert("正在执行 " + CURRENT_RPC +"请稍后再试！");
                                                    return false;
                                                }else{
                                                    window.location.href = element.href;
                                                    return true;
                                                }
                                                
                                            }

        
    }
}


/*
 *函数功能：发送服务器Ajax异步请求函数
 *参数：
 *  buttons：调用该函数的button对象
 *返回值：无
*/
function sendAjaxRequest(buttons){
    var rpc_name = buttons.name;
    
    if (!SET_FALG_HREF){  // 给超级链接添加检查是否执行的方法
        setHref();
        SET_FALG_HREF = true;
    }
    
    if (!rpc_name){
        alert("请选择要执行的rpc方法，在尝试！");
        return;
    }
    
    CURRENT_RPC = rpc_name
    var args = getFormValue();
    args["rpc_name"] = rpc_name;
    var isneedtoKillAjax = true;  // 检查ajax请求是否返回
    var url = getURL(rpc_name);

    if (AJAX_LOCK){
        alert("正在读取数据，请稍后……");
        return;
    }else{
        AJAX_LOCK = true;
    }    
    
    // 设定定时器判断ajax是否返回
    setTimeout(function(){
        checkAjaxTimeout();
    },AJAXLOCK_TIMEOUOT);
    
    $("#executingbar").show();
    
    var myAjaxCall = $.getJSON(url,
                               args,
                               function(json_data, textStatus){
                                 
                                 AJAX_LOCK = false;
                                 isneedtoKillAjax = false;
                                
                                 if (textStatus == "success"){
                                    refreshResult(json_data);
                                 }
                                 else{
                                    var err_data = "执行rpc方法失败：发送ajax请求失败！"
                                    exce_error(err_data)
                                 }
                               }
                             );
    
    // 检查是否ajax请求是否超时
    function checkAjaxTimeout(){
        if (isneedtoKillAjax){
            myAjaxCall.abort()
            AJAX_LOCK = false;
            ajaxTimeoutHandle();
        }
    }
}

function ajaxTimeoutHandle(){
    var err_data = "执行rpc方法失败：发送ajax请求超时，请重试！"
    exce_error(err_data)
}


/*
 *函数功能：处理客户端执行失败，组装失败信息函数
 *参数：
 *  err_data：执行失败的错误信息
 *返回值：无
*/
function exce_error(err_data){
    var json_data = {};
    
    json_data["exec_flag"] = "执行失败";
    json_data["exec_code"] = "9999";
    json_data["exec_ret"] = err_data;
    
    refreshResult(json_data)
}

/*
 *函数功能：更新执行结果内容
 *参数：
 *  json_data：json格式的数据包含执行成功与否标志;错误代码；执行结果
 *返回值：无
*/
function refreshResult(json_data){
    $("#executingbar").hide();
    document.getElementById("result_flag").innerHTML = json_data.exec_flag
    document.getElementById("result_code").innerHTML = json_data.exec_code
    document.getElementById("result_srtdata").innerHTML = json_data.exec_ret
}