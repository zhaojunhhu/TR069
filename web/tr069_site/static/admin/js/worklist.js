var dict_worklist_args = {};        // 保存工单参数
var dict_worklist_doc  = {};        // 保存工单描述
var list_worklist_template = [];    // 保存工单模板列表（树节点列表）
var current_node       = ""         //记录当前操作节点
var WORKLIST_NAME      = "";        // 保存当前的工单名称
var AJAX_LOCK          = false;     // 锁定是否正在进行ajax请求
var AJAXLOCK_ADDWORKLIST_TIMEOUOT  = 1000*530;  // django跟acs的超时时间设置为530s是因为acs跟用户的超时时间为520
var AJAXLOCK_GETWORKLISTTEMP_TIMEOUOT  = 1000*90; // 浏览器和Django服务器交互超时时间

TREE_OBJ       = ""
SELECT_WINDOWS = ""   // 选择授权用户的弹窗对象

Ext.require('Ext.tree.Panel');
Ext.require('Ext.data.TreeStore');
Ext.require('Ext.data.Store');


// 绑定工单文档按钮事件
$(document).on("click", "#id_workliist_doc_but", function(){

    var path          = getNodePath(current_node);
    var worklist_doc  = dict_worklist_doc[path];
    var worklist_name = current_node.data.text;
    var worklist_html = getWorklistDoc(worklist_doc)

    try{
       window.parent.newWindow(worklist_name, worklist_html)
    }catch(error){  }

})

/*
 *函数功能：获取提交工单的url地址
 *参数：无
 *返回值：
 *  url：组建好的url地址
*/
function getAddWorklistURL(){
    var url = $("#form_id").attr("action");
    return url+WORKLIST_NAME+"/"
}

/*
 *函数功能：获取获取工单模板的url地址
 *参数：无
 *返回值：
 *  url：组建好的url地址
*/
function getWorklistTemplateURL(){
    var url = "/itms/get_worklist_template/";

    return url
}

/*
 *函数功能：查找列表值的位置
 *参数：
 *  list_data：要查找的列表
 *  value：要查的列表中的值
 *返回值：
 *  number：小于0表示该值不存在列表中，大于等于0表示该值在列表中的位置
*/
function indexOfList(list_data, value){
    for (var i = 0; i < list_data.length; i++) {
        if (list_data[i] == value) return i;
    }
    return -1
}

/*
 *函数功能：删除列表中指定值
 *参数：
 *  list_data：要查找的列表
 *  value：要查的列表中的值
 *返回值：
 *  number：小于0表示该值不存在列表中删除失败
*/
function removeList(list_data, value){
    var index = indexOfList(list_data, value)
    if (index >-1){
        list_data.splice(index, 1);
        return value
    }else{
        return -1;
    }
}

/*
 *函数功能：清理本地保存的工单树信息及工单参数
 *参数：
 *  node：当前选择的树节点对象
 *返回值：
 *  url：组建好的url地址
*/
function clearSaveData(node){
    var path = getNodePath(node)
    // 如果选择的是到工单一层则删除dict_worklist_args字典中工单参数
    if (node.data.leaf){
        for (key in dict_worklist_args){
            if (key == path){
                delete dict_worklist_args[key];  // 删除保存的工单参数
                delete dict_worklist_doc[key];   // 删除保存的工单描述
            }
        }

    }else{ // 如果是工单树列表则删除在列表list_worklist_template中的值，并递归删除之节点信息
        var list_child = node.childNodes
        for (index in list_child){
            clearSaveData(list_child[index])
        }
        removeList(list_worklist_template, path);

    }
}

/*
 *函数功能：添加工单列表或者工单参数
 *参数：
 *  node：当前选中的树节点
 *返回值：无
*/
function addWorklistNode(node){
    clearSaveData(node); // 清理当前节点已访问过的信息
    node.removeAll();

    var list_worklist_nodes = getNodePathList(node);  // 获取要节点路径列表
    getWorklistTemplate(node, list_worklist_nodes);
}

/*
 *函数功能：获取工单列表或者工单参数
 *参数：
 *  node：                当前选中的树节点
 *  list_worklist_nodes： 取要节点路径列表
 *返回值：无
*/
function getWorklistTemplate(node, list_worklist_nodes){
    var args = {list_data:list_worklist_nodes};
    var url = getWorklistTemplateURL();
    var branch_flag = "getworklisttemplate";
    var timeout = AJAXLOCK_GETWORKLISTTEMP_TIMEOUOT;

    requestAjaxHandle(args, url, branch_flag, timeout, node);

}

/*
 *函数功能：处理Ajax返回的工单模板信息
 *参数：
 *  node：      当前选中的树节点
 *  json_data： django返回的json格式工单模版信息，json_data数据格式{exec_flag, exec_data}
 *返回值：无
*/
function addWorklistTemplate(node, json_data){
    // 当获取工单模板信息失败后的处理
    if (json_data.exec_flag != "success"){
        exceError(json_data.exec_data, node);
        return
    }

    var node_path    = getNodePath(node);
    var ret_data     = json_data.exec_data;
    var worklist_doc = json_data.worklist_doc;

    // 当获取到工单参数后在参数面板中显示参数并保存参数到本地
    if (node.data.leaf){
        var worklist_name = node.data.text;

        current_node = node;

        addArgs(worklist_name, ret_data);
        dict_worklist_args[node_path] = ret_data;

        if (worklist_doc){
            dict_worklist_doc[node_path] = worklist_doc;
        }
    }else{
        // 添加工单列表树中的节点，并保存相应信息到本地
        addNode(node, node_path, ret_data);
        list_worklist_template.push(node_path);
    }

}

/*
 *函数功能：工单树中添加工单信息列表
 *参数：
 *  node：      当前选中的树节点
 *  node_path： 当前节点在树中的路径
 *  list_data:  当前节点子节点名列表
 *返回值：无
*/
function addNode(node, node_path, list_data){
    // 当前如果树的层级大于等于3表明到工单一级没有子节点
    if (node.data.depth >= 3){
        var leaf_value = true;
    }else{
        var leaf_value = false;
    }
    for (i in list_data){
        var text_value       = list_data[i];
        var id = node_path+"/"+text_value;

        if (leaf_value){
            node.appendChild({id:id, text:text_value,qtip:text_value, leaf:leaf_value})
        }else{
            node.appendChild({id:id, text:text_value, leaf:leaf_value});
        }

    }
    node.expand()
}

/*
 *函数功能：双击修改输入框的样式事件
 *参数：
 *  input_args：html <input>对象
 *返回值：无
*/
function changeArgsCss(input_args){
    input_args.value="";
    input_args.style.color="#000000";
}

/*
 *函数功能：单击修改输入框颜色样式
 *参数：
 *  input_args：html <input>对象
 *返回值：无
*/
function changeAgsColor(input_args){
    input_args.style.color="#000000";
}

/*
 *函数功能：添加工单参数控件
 *参数：
 *  list_args_data: 工单参数列表
 *  worklist_name：当前工单名字
 *返回值：无
*/
function addArgs(worklist_name, list_args_data){
    $("#worklist_title").empty();

    $("#worklist_title").html("当前工单:" + worklist_name);
    try{
        $(".worklist_samp").remove();
    }catch(error){

    }

    $("#worklist_title_label").append("<samp class='worklist_samp'><input  type='button' id='id_workliist_doc_but' value='工单描述' /></samp>")

    WORKLIST_NAME = worklist_name;

    $('#args_table_id').empty();

    $('#physic_or_logic_div').show();

    document.getElementById("radio_physic_id").checked = true;

    $('#physic_or_logic_args_div').hide();

    for (var i in list_args_data){

        $("#args_table_id").append("<tr syple='padding-right:100px;'>"
                        +"<td align='left' styple='height:30px' text-indent='8px'>"+list_args_data[i][0]+":</td>"
                        +"<td align='left'><input calss='input_args' style='width:200px; color:#666666'"+
                        "onDblClick='changeArgsCss(this)' onClick='changeAgsColor(this)' type='text' name='"+ list_args_data[i][0]+"' value='"+list_args_data[i][1]+"'/>"+"</td>"
                        +"</tr>"
                   )
    }
}

/*
 *函数功能：添加工单描述信息
 *参数：
 *  list_args_data: 工单参数列表
 *  worklist_name：当前工单名字
 *返回值：无
*/
function getWorklistDoc(list_worklist_doc){

    var html_data = "<div id='id_div_worklist_doc' algin='center'>";

    for (index in list_worklist_doc){
        var data = list_worklist_doc[index]
        if (typeof(data) == "string"){
            html_data += "<p>"+data+"</p>"
        }else{
            html_data += "<table id=table_" + index + " border='1'>"
            for (index_two in data){
                if (index_two == '0' && data[0].length==3){
                    html_data += "<tr>";
                    html_data +="<td  nowrap='nowrap'>序号</td>"
                    html_data +="<td  nowrap='nowrap'>名称</td>"
                    html_data +="<td  nowrap='nowrap'>默认值</td>"
                    html_data +="<td  nowrap='nowrap'>描述</td>"
                    html_data += "</tr>";
                }else if (index_two == '0' && data[0].length==2){
                    html_data += "<tr>";
                    html_data +="<td  nowrap='nowrap'>序号</td>"
                    html_data +="<td  nowrap='nowrap'>SSID</td>"
                    html_data +="<td  nowrap='nowrap'>WAN连接操作</td>"
                    html_data += "</tr>";
                }

                html_data += "<tr>"

                var index = Number(index_two) + 1
                html_data +="<td  nowrap='nowrap'>" + index + "</td>"
                for (index_three in data[index_two]){
                    var temp_data = data[index_two][index_three]
                    html_data +="<td  nowrap='nowrap'>" + temp_data + "</td>"

                }
                html_data +="</tr>"
            }
            html_data +="</table></div>"

        //$("#args_doc_div").append(html_data)
        }
    }
    return html_data;
}
/*
 *函数功能：获取指定form中的所有的<input>
 *参数：
 *  formId：表单id值
 *返回值：
 *  elements：<input>对象列表
*/
function getElements(formId) {
    var form = document.getElementById(formId);
    var elements = new Array();
    var tagElements = form.getElementsByTagName('input');
    for (var j = 0; j < tagElements.length; j++){
         elements.push(tagElements[j]);
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
    var elements = getElements("form_id");
    var dict_args = {};

    var index = 1;   // 已1为起点和rf和工单模板中序列保持一致 zsj 2014-6-10
    for (i in elements){
        var element = elements[i];

        switch (element.type.toLowerCase()){
            case 'text':
                var value = element.value;
                if(value.toUpperCase() == "NULL"){
                    value = ""
                }
                dict_args[element.name] = [value, index+""];
                break;
            case 'radio':
                if (element.checked)
                    dict_args[element.name] = [element.value, index+""];
        }
        index += 1;
    }
    return dict_args;
}

/*
 *函数功能：添加工单，发送服务器Ajax异步请求函数
 *参数：无
 *返回值：无
*/
function addWorklist(){
    var args = getFormValue();
    var url = getAddWorklistURL();
    var timeout = AJAXLOCK_ADDWORKLIST_TIMEOUOT;
    var branch_flag = "addworklist";

    requestAjaxHandle(args, url, branch_flag, timeout)
}

/*
 *函数功能：发送Django服务器ajax请求并对执行结果做相应的处理
 *参数：
 *  args：发往服务器的参数值
 *  url：发往服务器的地址
 *  branch_flag：标识是工单模板查询还是新增工单
 *  timeout：ajax的超时时间，获取工单模板信息和新增工单时间不同
 *  node：可选参数，当在查询工单模板参数时需要
 *返回值：无
*/
function requestAjaxHandle(args, url, branch_flag, timeout, node){

    if ((branch_flag=="addworklist") && (!WORKLIST_NAME)){
        alert("请选择要添加的工单！");
        return;
    }

    var isneedtoKillAjax = true;  // 检查ajax请求是否返回

    if (AJAX_LOCK){
        alert("正在读取数据，请稍后……");
        return;
    }else{
        AJAX_LOCK = true;
    }

    // 设定定时器判断ajax是否返回
    setTimeout(function(){
        checkAjaxTimeout();
    },timeout);

    $("#loadbar").show();

    var myAjaxCall = $.getJSON(url,
                               args,
                               function(json_data, textStatus){

                                 AJAX_LOCK = false;
                                 isneedtoKillAjax = false;

                                 if (textStatus == "success"){
                                    if (branch_flag == "addworklist"){
                                        goWorklistInfo(json_data);
                                    }else{
                                        addWorklistTemplate(node, json_data)
                                    }
                                 }
                                 else{
                                     exceError("发送ajax请求失败！", node)
                                 }
                                 $("#loadbar").hide();
                               }
                             );

    // 检查是否ajax请求是否超时
    function checkAjaxTimeout(){
        if (isneedtoKillAjax){
            myAjaxCall.abort()
            AJAX_LOCK = false;
            ajaxTimeoutHandle(node);
        }
    }
}

/*
 *函数功能：处理ajax请求超时函数
 *参数：
 *  node：可选参数，当在查询工单模板参数超时时需要
 *返回值：无
*/
function ajaxTimeoutHandle(node){
    $("#loadbar").hide();

    if (node){
        var str_data = "获取工单模板信息失败：发送ajax请求超时，请重试！"
    }else{
        var str_data = "新增工单失败：发送ajax请求超时，请重试！"
    }
    exceError(str_data, node)
}

/*
 *函数功能：对django服务器返回新增工单成功与否的处理，成功调整到工单信息页面
 *参数：
 *    json_data: json数据格式{exec_flag, exec_ret}
 *返回值：无
*/
function goWorklistInfo(json_data){
    if (json_data.exec_flag == "success"){
        var pathname = window.location.pathname
        var revert = pathname.split('/')[3]
        var url =  "/itms/"+ json_data.exec_ret +  "/theworklistinfo/" + revert +"/"
        try{
            window.location.replace(url);
        }catch(e){
            alert(e)
        }

    }else{
        alert("新增工单 " + WORKLIST_NAME + " 失败("+ json_data.exec_ret+")，请重试！")
    }
}

/*
 *函数功能：对错误信息做提示
 *参数：
 *    err_data: 错误信息
 *返回值：无
*/
function exceError(err_data, node){
    if ((node) && (!node.data.leaf)){
        node.collapse();
    }
    alert(err_data)
}

/*
 *函数功能：切换工单类型（逻辑工单还是物理工单），改变用户名密码的显示
 *参数：
 *    redio: html的redio控件对象
 *返回值：无
*/
function showHiddenLogicArgs(redio){
    if (redio.value == "physic"){
        $('#physic_or_logic_args_div').hide()
    }else{
        $('#physic_or_logic_args_div').show()
    }
}

/*
 *函数功能：获取工单树的设备运营商
 *参数:无
 *返回值：
 *  node_worklists：树节点格式的数据
*/
function getWorkListIsp(){
    var list_worklist_isp = this.list_worklist_isp;
    var node_worklists = [];

    for (i in list_worklist_isp){
        node_worklists.push({text:list_worklist_isp[i], leaf:false});
    }


    return node_worklists
}

/*
 *函数功能：获取当前节点路径列表，倒序
 *参数:无
 *返回值：
 *  ret_list_data：前节点路径列表
*/
function getNodePathList(node){
    var ret_list_data = [];

    while (true){
        if (!node.data.root){
            ret_list_data.push(node.data.text);
            node = node.parentNode;
            continue;
        }
        break;
    }

    ret_list_data.reverse()
    return ret_list_data
}

/*
 *函数功能：获取当前节点路径
 *参数:无
 *返回值：
 *  node_path：获取当前节点路径
*/
function getNodePath(node){
    var node_path = "";

    while (true){
        if (!node.data.root){
            node_path = node.data.text + "/" + node_path;
            node = node.parentNode;
            continue;
        }
        break;
    }

    return node_path

}

/*
 *函数功能：检查节点是否被更新过
 *参数：
 *    node：当前树节点对象
 *返回值：
 *    true ： 没有被更新
 *    false： 已没有更新
*/
function checkNode(node){
    var path = getNodePath(node);
    var flag = true;

    if (node.data.leaf){
        var temp_data = dict_worklist_args;
    }else{
        var temp_data = list_worklist_template;
    }

    for(index_or_path in temp_data){
        // 当该node为叶子节点时index_or_path表示改节点路径，
        if (index_or_path == path){
            var worklist_name = node.data.text;

            current_node = node;

            addArgs(worklist_name, temp_data[index_or_path]); // 更新工单参数面板

            flag = false;
            break;
        }else if(temp_data[index_or_path] == path){
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
 *函数功能：双击节点事件；
 *参数：
 *    node: 当前节点对象
 *返回值：无
*/
function doubleClickNode(node){
    if (checkNode(node)){
        addWorklistNode(node);
    }
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

    var foldNode = {
            text:"展开",
            handler:function(){
                //当点击时隐藏右键菜单
                this.up("menu").hide();
                if(record.isExpanded()){
                    record.collapse();
                }else{
                    record.expand();
                    if (checkNode(record)){
                        doubleClickNode(record);
                    }
                }
            }
        };

    var refresh = {
        text:"刷新",
        handler:function(){
            var path = getNodePath(record)
            this.up("menu").hide();
            addWorklistNode(record);
        }
    };

    var items = [foldNode, refresh]

    var menu = new Ext.menu.Menu({
        //控制右键菜单位置
        float:true,
        items:items
    }).showAt(e.getXY());//让右键菜单跟随鼠标位置
}

/*
 *函数功能：当选中树某个节点前触发该事件；
 *参数：无
 *返回值：无
*/
function judgeLock(record){
    if (AJAX_LOCK){
        alert("正在读取数据，请稍后……")
    }
}

/*
 *函数功能：构造工单树；
 *参数：无
 *返回值：无
*/
Ext.onReady(function() {
    Ext.QuickTips.init();
    var treestore = Ext.create('Ext.data.TreeStore', {
        root: {
            expanded: true,
            children:getWorkListIsp()
        }
    });

    TREE_OBJ = Ext.create('Ext.tree.Panel', {
            title: '工单列表',
            autoWidth:true,
            height:600,
            renderTo: 'worklist-div',
            store : treestore,
            rootVisible: false,
            autoScroll:true,
            listeners:{
                itemexpand:function(record){
                    doubleClickNode(record);
                },
                itemcollapse:function(record){
                    doubleClickNode(record);
                },
                itemcontextmenu:function(view,record,item,index,e,eOpts){
                    this.getSelectionModel().select(record);
                    clickRight(view,record,item,index,e,eOpts);
                },
                beforeselect:function(view,record,index,eOpts){
                    judgeLock(record);
                },
                itemdblclick:function(view,record,item,index,e,eOpts){
                    if (record.data.leaf){
                        doubleClickNode(record);
                    }else if (checkNode(record) && !AJAX_LOCK){
                        doubleClickNode(record);
                    }else{
                        return;
                    }
                }
            }
        });
})
