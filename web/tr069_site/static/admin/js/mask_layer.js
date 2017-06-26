$(function () {

    $("#notichange").click(function(){  //  id=notichange的复选框的选中和非选中动作

        if ($("#notichange").is(":checked")){
            $("input[type='radio']").removeAttr('disabled');
        }
        else{
            $("input[type='radio']").attr('disabled',"true");
        }

    });
    
    $("#accesschange").click(function(){  //  id=accesschange的复选框的选中和非选中动作

        if ($("#accesschange").is(":checked")){
            $("input[name='2']").removeAttr('disabled');
        }
        else{
            $("input[name='2']").attr('disabled',"true");
        }
    });
})


/*
 *函数功能：弹出隐藏层
 *参数：
 *        show_div:弹出层
 *		  bg_div：背景层
 *返回值：
*/
function ShowDiv(show_div,bg_div){
document.getElementById(show_div).style.display='block';
document.getElementById(bg_div).style.display='block' ;
var bgdiv = document.getElementById(bg_div);
bgdiv.style.width = document.body.scrollWidth;
// bgdiv.style.height = $(document).height();
$("#"+bg_div).height($(document).height());
};


/*
 *函数功能：关闭弹出层
 *参数：
 *        show_div:弹出层
 *		  bg_div：背景层
 *返回值：
*/
function CloseDiv(show_div,bg_div)
{
document.getElementById(show_div).style.display='none';
document.getElementById(bg_div).style.display='none';
};