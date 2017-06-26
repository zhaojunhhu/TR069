var lock = false;           // 锁定是否正在进行ajax请求
var ajastimeout = 1000*530;  // django跟acs的超时时间设置为530s是因为acs跟用户的超时时间为520
var list_path = [];         // 放入已进行双击监听节点路径列表
var dic_leafnode={};         // 保存叶子节点供显示参数使用
var currentrecord             //记录当前操作节点
Ext.require('Ext.tree.Panel')
Ext.require('Ext.data.TreeStore')
Ext.require('Ext.data.Store')

/*
 *函数功能：更新参数树节点的子节点。
 *参数：
 *    node：     当前树节点对象；
 *    args：     发送给送服务器的参数；
 *    json_data：服务器发回给用户的json格式的数据{exec_flag：success/fail;
 *                            exec_ret:[[node_text,"true/fale"],……]；
 *                            exce_code；
 *                            }
 *返回值：无
*/
function addChildernNode(node, args, json_data){
    var path=args.ParameterPath;
    var ret_flag = json_data.exec_flag;
    
    if (ret_flag == "success"){
        nLeafnode(args.ParameterPath);
        var list_data = json_data.exec_ret;
        $("#paras").show();
        $("#par-val").show();
        $("#save").show();
        var tmp_flag = true
        var list_leafnode = []
        
        for (i in list_data){
            var leaf_value = false;
            
            var data       = list_data[i];
            var text_value = data[0];
                
            if (data[1] == "true"){
                leaf_value = true;
                list_leafnode.push(text_value);
            };
            node.appendChild({id: path+text_value, text:text_value, leaf:leaf_value});
        }
        dic_leafnode[path] = list_leafnode
        
    }else{
        addChilderenFail(path, json_data);
        return;
    }
    node.expand()
}


/*
 *函数功能：添加子节点失败时返回错误信息。
 *参数：
 *    path：     当前操作节点路径；
 *    json_data：服务器发回给用户的json格式的数据{exec_flag：success/fail;
 *                            exec_ret:[[node_text,"true/fale"],……]；
 *                            exce_code；
 *                            }
 *返回值：无
*/
function addChilderenFail(path, json_data){
        //执行失败则显示错误表格，包含错误代码，错误信息等
        $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                            +"<td style='width: 40%; text-indent:8px;'>执行失败"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>错误代码"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>"+json_data.exec_code+"</td>"
                        +"</tr>");
        $("#tab2").replaceWith("<tr id='tab2'>"
                                +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                                +"<td colspan='3' style='width: 80%; text-indent:8px;'>"+json_data.exec_ret+"</td>"
                            +"</tr>");
        $("#tab3").replaceWith("<tr id='tab3'>"
                            +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                            +"<td id='pathvalue' colspan='3' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                        +"</tr>");
    $("#attr").hide();
    $("#add").show();
    $("#del").show();
    $("#save").hide();
    $("#paras").hide();
    $("#par-val").hide();
}

/*
 *函数功能：获取值
 *参数：
 *    json_data：服务器发回给用户的json格式的数据
 *    
 *返回值：
 *    返回节点值
 *    
*/
function refreshResult(json_data){
    var result_data=json_data.exec_ret;
    var result=result_data[0];
    if (result[1] == null){
        result[1] = ""
    }else if(result[1] == "NULL"){
        result[1] = ""
    }else if(result[1] == "Null"){
        result[1] = ""
    }else if(result[1] == "None"){
        result[1] = ""
    }
    return result[1]
}
/*
 *函数功能：获取多个参数值取得ajax响应之后的操作
 *参数：
 *    args：服务器返回的参数
 *    json_data：服务器发回给用户的json格式的数据
 *返回值：
 *    无 
*/
function multiValues(args, json_data){
    
    var ret_flag = json_data.exec_flag;
    
    if (ret_flag == "success"){
        var a=$("input[name='checkbox']:checked").size();//计算选中行数
        var list_data = json_data.exec_ret
        var list_value = []
        for (i = 0; i<a; i++) {
            list_value.push(list_data[i][1])
        }
        
        $("input[name='checkbox']:checked").each(function(){ 
            var tablerow=$(this).closest("tr");
            var par_val=tablerow.find("input[type='text']");
            par_val.val(list_value.pop());
        })
    }else{
        alert("获取参数值失败！")
    }
}
/*
 *函数功能：检查节点是否被更新过
 *参数：
 *    path：树节点的完全路径
 *    node：当前树节点对象
 *返回值：
 *    true ： 已经被更新
 *    false：    没有更新 
*/
function checkNode(node, path){
    if(!path){
        path = getNodePath(node);
    }
    var flag = true
    for(var i=0; i<list_path.length; i++){
        if(list_path[i] == path ){
            if(!node.isExpanded()){
                node.collapse();
            }else{
                node.expand(); 
            }
            flag = false
            break;
        }
    }
    return flag
}

/*
 *函数功能：保存参数的值。
 *参数：
 *    
 *    args：服务器返回的参数
 *    json_data：服务器发回给用户的json格式的数据
 *                            
 *                             
 *返回值：无
*/
function setValues(args, json_data){
    var ret_flag = json_data.exec_flag;//读取返回的执行成功与否标志
    if (ret_flag == "success"){
    $('#tab1 td').empty();
    $('#tab2 td').empty();
    $('#tab3 td').empty();
    $("#tab1").replaceWith("<tr id='tab1'>"
                        +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                        +"<td colspan='3' style='width: 80%; text-indent:8px;'>执行成功"+"</td>"
                    +"</tr>");
    }
    else {
        //执行失败则显示错误表格，包含错误代码，错误信息等
        $('#tab3 td').empty();
        $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                            +"<td style='width: 40%; text-indent:8px;'>执行失败"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>错误代码"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>"+json_data.exec_code+"</td>"
                        +"</tr>");
        $("#tab2").replaceWith("<tr id='tab2'>"
                                +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                                +"<td colspan='3' style='width: 80%; text-indent:8px;'>"+json_data.exec_ret+"</td>"
                            +"</tr>");
    }
}

/*
 *函数功能：获取参数属性。ajax请求完成之后显示修改参数属性对话框
 *参数：
 *    
 *    node:节点
 *    args:服务器返回的参数
 *    json_data:服务器发回给用户的json格式的数据
 *                            
 *                            
 *返回值：无
*/
function getAttributes(node, args, json_data){
    var ret_flag = json_data.exec_flag;
    
    if (node){
        var path = getNodePath(node);
    }else{
        var path = getNodePath(currentrecord);
        if(!currentrecord.data.leaf){//如果不是叶子节点则保证path最后以为为'.'
                if(path.slice(-1)!="."){
                path = path+'.'
            }
        }
    }
    if (ret_flag == "success"){//成功时
        //读取NotificationChange的值，用以显示
        var dict_data = json_data.exec_ret;
        if (dict_data["NotificationChange"] == 1){
            $("input[type='radio'][name='1']").removeAttr('disabled');//NotificationChange=1的时候移除radio 的disabled属性
            $("#notichange").attr("checked",'true');
        }else{
            $("input[type='radio'][name='1']").attr('disabled',"true"); 
            $("#notichange").removeAttr("checked");
        }
        //读取Notification的值，用以显示
        if (dict_data["Notification"] == 0){
            $("input[type='radio'][value='off']").attr("checked",'true');
        }else if (dict_data["Notification"] == 1){
            $("input[type='radio'][value='passive']").attr("checked",'true');
        }else if (dict_data["Notification"] == 2){
            $("input[type='radio'][value='active']").attr("checked",'true');
        }
        //读取AccessListChange的值，用以显示
        if (dict_data["AccessListChange"] == 1){
            $("input[type='checkbox'][name='2']").removeAttr('disabled');//AccessListChange=1的时候移除checkbox的disabled属性
            $("#accesschange").attr("checked",'true');
        }else{
            $("input[type='checkbox'][name='2']").attr('disabled',"true");
            $("#accesschange").removeAttr("checked");
        }
        //读取Acclist的值，用以显示
        var list_string = dict_data["AccessList"];
        for (var i in list_string){
            if (list_string[i] == "Subscriber"){
                $("#subscriber").attr("checked",'true');
            }else {
                $("#subscriber").removeAttr("checked");
            }
            
        }
        if (list_string.length == 2){
            $("#baretext").attr("checked",'true');
            $("#baretext").val(list_string[1]);
        }else{
            $("#baretext").removeAttr("checked");
        }
        //
        $("#paraName").replaceWith(
            "<td id='paraName' colspan='3'>"+path+"</td>"
        );
        ShowDiv('MyDiv','fade')//显示遮罩层
        }else{//失败时
        $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                            +"<td style='width: 40%; text-indent:8px;'>执行失败"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>错误代码"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>"+json_data.exec_code+"</td>"
                        +"</tr>");
        $("#tab2").replaceWith("<tr id='tab2'>"
                                +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                                +"<td colspan='3' style='width: 80%; text-indent:8px;'>"+json_data.exec_ret+"</td>"
                            +"</tr>");
        $("#tab3").replaceWith("<tr id='tab3'>"
                            +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                            +"<td id='pathvalue' colspan='3' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                        +"</tr>");
        }

}

/*
 *函数功能：设置参数属性获得服务器返回结果后的处理
 *参数：
 *    
 *    node:节点
 *    args:服务器返回的参数
 *    json_data:服务器发回给用户的json格式的数据
 *                            
 *                            
 *返回值：无
*/

function setAttributes(node, args, json_data){
    CloseDiv('MyDiv','fade');//执行完成后关闭遮罩层
    var ret_flag = json_data.exec_flag;
    var list_data = args["ParameterList"];//取出参数属性值
        
    if (node){
        var path = getNodePath(node);
    }else{
        var path = getNodePath(currentrecord);
        if(!currentrecord.data.leaf){//如果不是叶子节点则保证path最后以为为'.'
                if(path.slice(-1)!="."){
                path = path+'.'
            }
        }
    }
    if (ret_flag == "success"){//成功时
    $('#tab1 td').empty();
    $('#tab2 td').empty();
    $('#tab3 td').empty();
    $("#tab1").replaceWith("<tr id='tab1'>"
                        +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                        +"<td colspan='3' style='width: 80%; text-indent:8px;'>执行成功"+"</td>"
                    +"</tr>");
    $("#tab2").replaceWith("<tr id='tab2'>"
                            +"<td style='width: 20%; text-indent:8px;'>属性值"+"</td>"
                            +"<td id='pathvalue' colspan='3' style='width: 80%; text-indent:8px;'>"
                            +"NotificationChange = "+list_data[0]+";&nbsp"
                            +"Notification = "+list_data[1]+";&nbsp"
                            +"AccessListChange = "+list_data[2]+";&nbsp"
                            +"AccessList = "+list_data[3]
                            +"</td>"
                        +"</tr>");
    $("#tab3").replaceWith("<tr id='tab3'>"
                            +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                            +"<td id='pathvalue' colspan='3' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                        +"</tr>");
    }else{//失败时
        $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                            +"<td style='width: 40%; text-indent:8px;'>执行失败"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>错误代码"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>"+json_data.exec_code+"</td>"
                        +"</tr>");
        $("#tab2").replaceWith("<tr id='tab2'>"
                                +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                                +"<td colspan='3' style='width: 80%; text-indent:8px;'>"+json_data.exec_ret+"</td>"
                            +"</tr>");
        $("#tab3").replaceWith("<tr id='tab3'>"
                            +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                            +"<td id='pathvalue' colspan='3' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                        +"</tr>");
    }
}

/*
 *函数功能：添加实例获得从服务器返回结果后的处理
 *参数：
 *    
 *    node:节点
 *    args:服务器返回的参数
 *    json_data:服务器发回给用户的json格式的数据
 *                            
 *                            
 *返回值：无
*/
function increaseObject(node, args, json_data){
    var ret_flag = json_data.exec_flag;
    if (node){
        var path = getNodePath(node);
    }else{
        
        var path = $("#tab1").find("td:eq(1)").text();//读取设备操作表格中参数名称
    }
    if (ret_flag == "success"){//成功时
            alert ("执行成功");
        var i = json_data.exec_ret.InstanceNumber;
        currentrecord.appendChild({id:path+i, text:i});//添加子节点
    }else{//失败时
        $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                            +"<td style='width: 40%; text-indent:8px;'>执行失败"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>错误代码"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>"+json_data.exec_code+"</td>"
                        +"</tr>");
        $("#tab2").replaceWith("<tr id='tab2'>"
                                +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                                +"<td colspan='3' style='width: 80%; text-indent:8px;'>"+json_data.exec_ret+"</td>"
                            +"</tr>");
        $("#tab3").replaceWith("<tr id='tab3'>"
                            +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                            +"<td id='pathvalue' colspan='3' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                        +"</tr>");
    }
    $("#paras").hide();
    $("#par-val").hide();
}


/*
 *函数功能：添加实例获得从服务器返回结果后的处理
 *参数：
 *    
 *    node:节点
 *    args:服务器返回的参数
 *    json_data:服务器发回给用户的json格式的数据
 *                            
 *                            
 *返回值：无
*/
function delObject(node, args, json_data){
    var ret_flag = json_data.exec_flag;
    if (node){
        var path = getNodePath(node);
    }else{
        var path = $("#tab1").find("td:eq(1)").text();
    }
    if (ret_flag == "success"){//成功时
        alert ("执行成功");
        currentrecord.remove(currentrecord);//删除子节点
        
    }else{//失败时
        $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                            +"<td style='width: 40%; text-indent:8px;'>执行失败"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>错误代码"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>"+json_data.exec_code+"</td>"
                        +"</tr>");
        $("#tab2").replaceWith("<tr id='tab2'>"
                                +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                                +"<td colspan='3' style='width: 80%; text-indent:8px;'>"+json_data.exec_ret+"</td>"
                            +"</tr>");
        $("#tab3").replaceWith("<tr id='tab3'>"
                            +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                            +"<td id='pathvalue' colspan='3' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                        +"</tr>");
    }
    $("#paras").hide();
    $("#par-val").hide();
}

/*
 *函数功能：重启设备获得从服务器返回结果后的处理
 *参数：
 *    
 *    args:服务器返回的参数
 *    json_data:服务器发回给用户的json格式的数据
 *                            
 *                            
 *返回值：无
*/
function rebootHandle(args, json_data){
    var ret_flag = json_data.exec_flag;
    if (ret_flag == "success"){//成功
        alert("操作成功")
    }else {//失败
        $('#tab3 td').empty();
        $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                            +"<td style='width: 40%; text-indent:8px;'>执行失败"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>错误代码"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>"+json_data.exec_code+"</td>"
                        +"</tr>");
        $("#tab2").replaceWith("<tr id='tab2'>"
                                +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                                +"<td colspan='3' style='width: 80%; text-indent:8px;'>"+json_data.exec_ret+"</td>"
                            +"</tr>");
    }
}


/*
 *函数功能：恢复出厂获得从服务器返回结果后的处理
 *参数：
 *    
 *    args:服务器返回的参数
 *    json_data:服务器发回给用户的json格式的数据
 *                            
 *                            
 *返回值：无
*/
function resetHandle(args, json_data){
    var ret_flag = json_data.exec_flag;
    if (ret_flag == "success"){//成功
        alert("操作成功")
    }else {//失败
        $('#tab3 td').empty();
        $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                            +"<td style='width: 40%; text-indent:8px;'>执行失败"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>错误代码"+"</td>"
                            +"<td style='width: 20%; text-indent:8px;'>"+json_data.exec_code+"</td>"
                        +"</tr>");
        $("#tab2").replaceWith("<tr id='tab2'>"
                                +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                                +"<td colspan='3' style='width: 80%; text-indent:8px;'>"+json_data.exec_ret+"</td>"
                            +"</tr>");
    }
}
/*
 *函数功能：发送服务器Ajax异步请求函数
 *参数：
 *    url：请求地址；
 *    args：请求参数
 *    node：树节点对象
 *    rpc_name: 处理分支标志
 *返回值：无
*/
function ajaxHandle(args, rpc_name, node){
    var isneedtoKillAjax = true;  // 检查ajax请求是否返回
    var url = getUrl();
    
    args.rpc_name = rpc_name;
    
    if (rpc_name != "GetParameterNames"){
        if (lock){
            alert("正在读取数据，请稍后……");
            return;
        }else{
            lock = true;
        }    
    }
    
    // 设定定时器判断ajax是否返回
    setTimeout(function(){
        checkAjaxTimeout();
    },ajastimeout);
    
    $("#loadbar").show();
    
    var myAjaxCall = $.getJSON(url,
                               args,
                               function(json_data, textStatus){
                                    $("#loadbar").hide();
                                    lock = false;
                                    isneedtoKillAjax = false;
                                       
                                     switch (rpc_name){
                                        case "GetParameterNames":
                                            addChildernNode(node, args, json_data);  // 更新树节点
                                            addtr(args.ParameterPath);            // 添加相应父节点下子节点的参数
                                            break;
                                        case "GetParameterValues":
                                            //refreshResult(json_data);
                                            var str_aa = args.ParameterNames;
                                            if(str_aa.slice(-1)!=","){
                                               leafnode(args.ParameterNames, json_data);
                                                break; 
                                            }else{
                                                multiValues(args, json_data)
                                                break;
                                            }    
                                        case "SetParameterValues":
                                            setValues(args, json_data);
                                            break;
                                        case "GetParameterAttributes":
                                            getAttributes(node, args, json_data);
                                            break;
                                        case "SetParameterAttributes":
                                            setAttributes(node, args, json_data);
                                            break;
                                        case "AddObject":
                                            increaseObject(node, args, json_data);
                                            break;
                                        case "DeleteObject":
                                            delObject(node, args, json_data);
                                            break;
                                        case "Reboot":
                                            rebootHandle(args, json_data);
                                            break;
                                        case "FactoryReset":
                                            resetHandle(args, json_data);
                                            break;
                                         default:
                                             alert("输入的请求不识别！")
                                     };
                                }
                               );
    // 检查是否ajax请求是否超时
    function checkAjaxTimeout(){
        if (isneedtoKillAjax){
            myAjaxCall.abort();
            ajaxTimeoutHandle();
            $("#loadbar").hide();
            lock = false;
        }
    }
}

/*
 *函数功能：对ajax请求超时做处理
 *参数：
 *     无
 *返回值：
 *    无
 *    
*/

function ajaxTimeoutHandle(){
    CloseDiv('MyDiv','fade');
    $('#tab3 td').empty();
    $("#tab1").replaceWith("<tr id='tab1'>"
                        +"<td style='width: 20%; text-indent:8px;'>操作结果"+"</td>"
                        +"<td style='width: 80%; text-indent:8px;'>执行失败"+"</td>"
                    +"</tr>");
    $("#tab2").replaceWith("<tr id='tab2'>"
                            +"<td style='width: 20%; text-indent:8px;'>错误描述"+"</td>"
                            +"<td colspan='3' style='width: 80%; text-indent:8px;'>连接服务器请求超时"+"</td>"
                        +"</tr>");
    
    return
    
}

/*
 *函数功能：获取当前节点的完全路径
 *参数：
 *    node： 树节点对象
 *返回值：
 *    path：树节点的完全路径
*/
function getNodePath(node){
    var path = node.data.text
    while (true){
        if (!node.data.root){
            node = node.parentNode;
            path = node.data.text+"." + path;
            continue;            
        }
        break;
    }
    return path
}

/*
 *函数功能：获取对应cpe的cpe_id，用于组建ajax请求的url
 *参数：无
 *返回值：cpe_id
*/
function getCPEID(){
    return this.cpe_id
}

/*
 *函数功能：获取对应发送的url
 *参数：无
 *返回值：cpe_id
*/
function getUrl(){
    return "/itms/"+ getCPEID() +"/ajax_rpc_request/"
}

/*
 *函数功能：获取cpe参数树的根节点
 *参数无：
 *返回值：rootText：参数树的根节点
*/
function getRootText(){
    return this.root_text;
}

/*
 *函数功能：保存参数值，即为按钮“保存参数”添加的动作
 *参数：
 *        无
 *返回值：
*/
function setParameterValues(){
    var rpc_name = "SetParameterValues"
    var args = {}
    
    var a=$("input[name='checkbox']:checked").size();//计算选中行数

    if(!a){
        alert("请至少选择一条记录进行保存！");//如果选中行数为0则弹出警告框
        return
    }
    else{                                     //否则执行保存参数动作
        
        var list_data = []
        $("input[name='checkbox']:checked").each(function(){
            var dict_args={};
            
            var tablerow=$(this).closest("tr");
            var set_val=tablerow.find("input[type='text']").val();
            var set_name=tablerow.find("td:eq(1)").text();
            
            list_data.push([set_name, set_val])
        })
        
        args["SetParameterValuesArgs"] = list_data;
    }
    ajaxHandle(args, rpc_name)
}

/*
 *函数功能：获取参数属性值，即为按钮“参数属性”添加的动作
 *参数：
 *        node：操作节点
 *返回值：
*/
function getParameterAttributes(node){
    var rpc_name = "GetParameterAttributes"
    
    if (node){
        var path = getNodePath(node);
    }else{
        //var current = currentrecord.parentNode;
        //var path = current.data.text + "." + currentrecord.data.text;
        //var path = $("#tab1").find("td:eq(1)").text();//读取设备操作表格中参数名称
        var path = getNodePath(currentrecord);
        if(!currentrecord.data.leaf){//如果不是叶子节点则保证path最后以为为'.'
                if(path.slice(-1)!="."){
                path = path+'.'
            }
        }
        }

    var args = {ParameterNames:path};
    
    ajaxHandle(args, rpc_name);
    }


/*
 *函数功能：修改参数属性，即点击参数属性表格确定按钮所触发的动作
 *参数：
 *        node：操作节点
 *返回值：返回参数属性
*/
function setParameterAttributes(node){
    var rpc_name = "SetParameterAttributes"
    if (node){
        var path = getNodePath(node);
    }else{
        //var path = $("#pathvalue").text();//读取设备操作表格中路径
        var path = getNodePath(currentrecord);
        if(!currentrecord.data.leaf){//如果不是叶子节点则保证path最后以为为'.'
                if(path.slice(-1)!="."){
                path = path+'.'
            }
        }
    }
    var attributesData = [];
    var args = {};
    var list_data = [];
    var dict_data = {};
    //获取NotificationChange复选框值
    
    if ($("#notichange").is(":checked")){
        list_data.push("1")
    }else{
        list_data.push("0")
    }
    //获取Notification值
    
    var radio = $("input[name='1']:checked").val();
    if (radio == "off"){
        list_data.push("0")
    }else if(radio == "passive"){
        list_data.push("1")
    }else if(radio == "active"){
        list_data.push("2")
    }
    //获取AccessListChange值
    if ($("#accesschange").is(":checked")){
        list_data.push("1")
    }else{
        list_data.push("0")
    }
    //获取AccessList值
    var AccessList = [];
    if ($("#subscriber").is(":checked")){
       AccessList.push("Subscriber")
    }
    if ($("#bare").is(":checked")){
        var baretext = $("#baretext").val();
        AccessList.push(baretext)
    }
    list_data.push(AccessList);

    list_data.push(path);
    args["ParameterList"] = list_data;
    ajaxHandle(args, rpc_name);
    
}

/*
 *函数功能：为参数列表添加数据行
 *参数：
 *    path：当前操作节点路径
 *返回值：无
*/
function addtr(path){
    //添加行数据之前先删除之前的行
    
    $('#patb tr').empty();
    if(path.slice(-1)!="."){
        path=path+'.'
    }
    var list_data = dic_leafnode[path];
    try{//list_data 为空时调用.length方法会报错
        var size=list_data.length; 
    }catch(error){
        var size = undefined;
    }
    
    if(size){//size不为空
        $("#paras").show();
        $("#par-val").show();
        $("#save").show();
        for (var i in list_data){
                
                $("#patb").append("<tr>"
                                +"<td align='center'><input type='checkbox' name='checkbox' />"+"</td>"
                                +"<td style='width:50%; text-indent:8px;'>"+path+list_data[i]+"</td>"
                                +"<td><input style='width:95%;' type='text' name='list_data[i]'/>"+"</td>"
                            +"</tr>")
        }
        nLeafnode(path);
    }
    else{//size为空
    $("#paras").hide();
    $("#par-val").hide();
    $("#save").hide();
        return
    }
}

/*
 *函数功能：双击非叶子节点时按钮和表格显示情况
 *参数：
 *    path：当前操作节点路径
 *返回值：无
*/
function nLeafnode(path){
    try{
        var aa = currentrecord.data.leaf;
    }catch(error){
        aa = undefined
    }
    if (!aa){//如果不是叶子节点
        
            //按钮的显示、隐藏
            $("#attr").hide();
            $("#add").show();
            $("#del").show();
            if(path.slice(0,-1) != getRootText()){
                $("#add").removeAttr('disabled');
                $("#del").removeAttr('disabled');
            }
            else{
                $("#add").attr('disabled',"true");
                $("#del").attr('disabled',"true");
            }
            
            //设备操作表格的处理
            $('#tab1 td').empty();
            $('#tab2 td').empty();
            $('#tab3 td').empty();
            $("#tab1").replaceWith("<tr id='tab1'>"
                                    +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                                    +"<td id='pathvalue' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                                +"</tr>");
        }
}
/*
 *函数功能：双击叶子节点时按钮和表格显示情况
 *参数：
 *    path：当前操作节点路径
 *    json_data:服务器发回给用户的json格式的数据
 *返回值：无
*/
function leafnode(path,json_data){
    if (currentrecord.data.leaf){
        
            $("#paras").hide();//隐藏id=paras的table
            $("#par-val").hide();
            $("#add").hide();
            $("#del").hide();
            $("#attr").show();
            var values=refreshResult(json_data);
            //设备操作表格的处理
            $('#tab1 td').empty();
            $('#tab2 td').empty();
            $('#tab3 td').empty();
            $("#tab1").replaceWith("<tr id='tab1'>"
                                    +"<td style='width: 20%; text-indent:8px;'>参数名称"+"</td>"
                                    +"<td id='pathvalue' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                                +"</tr>");
            $("#tab2").replaceWith("<tr id='tab2'>"
                                    +"<td style='width: 20%; text-indent:8px;'>参数值"+"</td>"
                                    +"<td style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+values+"</textarea>"+"</td>"
                                +"</tr>");
        }
}
/*
 *函数功能：双击节点事件；
 *参数：
 *    node: 当前节点对象
 *返回值：无
*/
function doubleClickNode(node){
    var path = getNodePath(node);
    
    if (node.isRoot()){
        refreshNode(node, path);
    }else if (!node.data.leaf){      // 判断是否有叶子节点,选择是否是取值操作
        if (checkNode(node, path)){  // 检查路径是否被打开过,如果没被打开过
            refreshNode(node, path);
            addtr(path, dic_leafnode);
        }else{                       //如果被打开过
            addtr(path, dic_leafnode);
            return
        }
    }else{
    getParameterValues(node,path);
    }
}

/*
 *函数功能：刷新当前节点的子节点
 *参数：
 *    node：当前树节点对象
 *    path:节点路径
*/
function refreshNode(node, path){
    var rpc_name = "GetParameterNames"
    if(!path){
        path = getNodePath(node);
    }
    
    if (lock){
        alert("正在读取数据，请稍后……");
        return;
    }else{
        lock = true;
    }
    
    node.removeAll();
    
    if (node.isRoot()){
        list_path = [];
        dic_leafnode={};
    }else{
        list_path.push(path);
    }
    
    path +=".";
    var args = {ParameterPath:path, NextLevel:"1"};
    $("#paras").hide();
    $("#par-val").hide();
    ajaxHandle(args, rpc_name, node);
    
}

/*
 *函数功能：刷新当前节点的子节点
 *参数：
 *    node：当前树节点对象
 *    path:节点路径
*/
function getParameterValues(node, path){
    var rpc_name = "GetParameterValues"
    if(!path){
        path = getNodePath(node);
    }
    
    var args = {ParameterNames:path};
    ajaxHandle(args, rpc_name, node)
}

/*
 *函数功能：发起ajax请求获取多个参数的值
 *参数：
 *    无
 *返回值：无
*/
function multiParameterValues(){
    var rpc_name = "GetParameterValues"
    var paths = ""
    
    var a=$("input[name='checkbox']:checked").size();//计算选中行数

    if(!a){
        alert("请至少选择一个参数！");//如果选中行数为0则弹出警告框
        return
    }else{
        var list_data = []
        $("input[name='checkbox']:checked").each(function(){
            
            var tablerow=$(this).closest("tr");
            
            var par_name=tablerow.find("td:eq(1)").text();
            
            paths = paths + par_name + ","  //paths为字符串，参数名用“,”隔开
        })
        var args = {ParameterNames:paths}
    }
    ajaxHandle(args, rpc_name)
}

/*
 *函数功能：请求重启cpe
*/
function reboot(){
    var rpc_name = "Reboot"
    
    var args = {};
    
    ajaxHandle(args, rpc_name)
}

/*
 *函数功能：请求cpe恢复出厂
*/
function factoryReset(){
    var rpc_name = "FactoryReset";
    
    var args = {};
    
    ajaxHandle(args, rpc_name)
}

/*
 *函数功能：请求对节点添加节点
 *参数：
 *    node：要添加子节点的节点对象
 *返回值：无
*/
function addObject(node){
    var rpc_name = "AddObject";
    
    if (node){
        var path = getNodePath(node) + "."
    }else{
        var path = $("#tab1").find("td:eq(1)").text();//读取设备操作表格中参数名称
    }
    var args = {ObjectName:path};
    
    ajaxHandle(args, rpc_name, node);
}

/*
 *函数功能：请求删除节点
 *参数：
 *    node：要删除的节点对象
 *返回值：无
*/
function deleteObject(node){
    var rpc_name = "DeleteObject";
    
    if (node){
        var path = getNodePath(node) + "."
    }else{
        var path = $("#tab1").find("td:eq(1)").text();//读取设备操作表格中参数名称
    }
    
    var args = {ObjectName:path};
    
    ajaxHandle(args, rpc_name, node);
    
}

/*
 *函数功能：右键菜单显示
 *参数：
 *    view：指向Ext.view.View
 *    record:当前的选项（当前的树节点）
 *    item：HTMLElement对象
 *    index：选项的索引
 *    e：事件对象
 *    eOpts：
 *返回值：无
*/
function clickRight(view,record,item,index,e,eOpts){
    //禁用浏览器的右键相应事件
    e.preventDefault();
    e.stopEvent();
    $("#add").removeAttr('disabled');//为添加实例按钮添加disabled属性
    $("#del").removeAttr('disabled');//为删除实例按钮添加disabled属性
    var path = getNodePath(record)+'.';
    //设备操作表格的处理
    $('#tab1 td').empty();
    $('#tab2 td').empty();
    $('#tab3 td').empty();
    $("#tab1").replaceWith("<tr id='tab1'>"
                            +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                            +"<td id='pathvalue' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                        +"</tr>");
    for(var i in list_path){//节点展开过
        var val = list_path[i];
        if (val == path){
            $('#paras').show();
            $("#par-val").show();
            $("#save").show();
        }else{
            $('#paras').hide();//隐藏参数列表
            $("#save").hide();
            $("#par-val").show();
        }
    }
    var refresh = {
            text:"刷新",
            handler:function(){
                //当点击时隐藏右键菜单
                this.up("menu").hide();
                refreshNode(record);
            }
        };
    
    var parameterValues = {
        text:"参数值",
        handler:function(){
            this.up("menu").hide();
            doubleClickNode(record);
        }
    };
    
    var foldNode = {
        text:"展开",
        handler:function(){
            var path = getNodePath(record)
            this.up("menu").hide();
            if(record.isExpanded()){
                record.collapse();
            }else{
                record.expand();
                for ( i in list_path){
                    if (list_path[i] == path){
                        return;
                    }
                }
                refreshNode(record, path);
            } 
        }
    };
    
    var addParameter = {
        text:"添加实例",
        handler:function(){
            this.up("menu").hide();
            addObject(record);
        }
    };
    
    var deleteParameter = {
        text:"删除实例",
        handler:function(){
            this.up("menu").hide();
            deleteObject(record);
        }
    };
    
    var var_reboot = {
    text:"重启设备",
    handler:function(){
        this.up("menu").hide();
        reboot();
    }
    };
    
    var var_factoryReset = {
        text:"恢复出厂",
        handler:function(){
        this.up("menu").hide();
        factoryReset();
        }
    };
    
    var items = [var_reboot, var_factoryReset]
    
    if (record.data.leaf){
        items.unshift(parameterValues);
    }else if (record.isRoot()){
        items.unshift(refresh);
    }else{
        items.unshift(deleteParameter);
        items.unshift(addParameter);
        items.unshift(foldNode);
        items.unshift(refresh);
    }
    
    var menu = new Ext.menu.Menu({
        //控制右键菜单位置
        float:true,
        items:items
    }).showAt(e.getXY());//让右键菜单跟随鼠标位置
}

    
/*
 *函数功能：判断是否可以选中节点
 *参数：
 *    
 *    record:当前的选项（当前的树节点）
 *返回值：无
*/
function judgeLock(record){
    if (lock){
        alert("正在读取数据，请稍后……")
    }else{
        currentrecord = record;
        //设备操作列表显示选中节点名字
            var path = getNodePath(currentrecord);
            if(!currentrecord.data.leaf){//如果不是叶子节点则保证path最后以为为'.'
                $('#add').show();
                $('#del').show();
                $('#attr').hide();
                if(path.slice(-1)!="."){
                path = path+'.'
            }
            }else{
                $('#add').hide();
                $('#del').hide();
                $('#attr').show();
            }
            $('#tab1 td').empty();
            $('#tab2 td').empty();
            $('#tab3 td').empty();
            $("#tab1").replaceWith("<tr id='tab1'>"
                                +"<td style='width: 20%; text-indent:8px;'>路径"+"</td>"
                                +"<td id='pathvalue' colspan='3' style='width: 80%'><textarea style='width:95%' rows = '1' readonly = 'readonly'>"+path+"</textarea>"+"</td>"
                            +"</tr>");
            $('#paras').hide();
            $("#save").hide();
            $("#par-val").hide();
        }
     
    }
Ext.onReady(function() {
    
    $(document).ready(function(){
       $("#paras").hide();//隐藏id=paras的table
       $("#par-val").hide();
       $("#attr").hide();//隐藏参数属性按钮
       $("#save").hide();//隐藏保存参数按钮
       $("#add").attr('disabled',"true");//为添加实例按钮添加disabled属性
       $("#del").attr('disabled',"true");//为删除实例按钮添加disabled属性
       $("#loadbar").hide();
    });
    //生成树时需要使用到的数据
    var treestore = Ext.create('Ext.data.TreeStore', {
    root: {
        text:getRootText(),
        expanded: false,
        collapsed:true,
        icon:"/static/treeroot.bmp"
    }
    });

    var tree = Ext.create('Ext.tree.Panel', {
        title: '动态参数树',
        id:'dyntree',
        //autoWidth:true,
        width:Ext.get("path-div").getWidth(),
        height:330,
        renderTo: 'tree-div',
        store : treestore,
        listeners:{
            itemexpand:function(record){
                doubleClickNode(record);
            },
            itemcollapse:function(record){
                doubleClickNode(record);
            },
            beforeselect:function(view,record,index,eOpts){
                judgeLock(record);
            },
            itemdblclick:function(view,record,item,index,e,eOpts){
                if (record.data.leaf){
                    getParameterValues(record);
                }else{
                    return;
                }
            },
            itemcontextmenu:function(view,record,item,index,e,eOpts){
                this.getSelectionModel().select(record);
                clickRight(view,record,item,index,e,eOpts);
            }
        }
    })
})




