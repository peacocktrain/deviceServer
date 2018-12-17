var wsUri ="ws://jorylee.com:8887/";

function init() {
    startWebSocket();
}
function startWebSocket() {
    websocket = new WebSocket(wsUri);
    websocket.onopen = function(evt) {
        onOpen(evt)
    };
    websocket.onclose = function(evt) {
        onClose(evt)
    };
    websocket.onmessage = function(evt) {
        onMessage(evt)
    };
    websocket.onerror = function(evt) {
        onError(evt)
    };
}
function onOpen(evt) {
    // 在连接时获取设备列表
    writeToTop("CONNECTED to " + wsUri);
    doSend("getDevices");
}
function onClose(evt) {
    writeToTop("DISCONNECTED to " + wsUri);
}
function onMessage(evt) {

    console.log(evt.data)
    o =  $.parseJSON( evt.data )

        // 获取设备列表
    if ( "getDevices" == o["function"] ){
        //writeToTop('<span style="color: gray;">'+ o['data'] +'</span>');
        layoutDevices(o['data'])
    }
        // 如果 为日志tail动作请求
    else if ( "tail" == o["function"] ){
        message = o['data']
        if ( preClickElement.attr("ip") == message["ip"]){
            writeToLog(  "<br/><span style='color: lightgray'>" + message["time"] + " ["+message["ip"]+"] </span><span style='color: green;'>" + message["line"] + "</span>" );
        }
    }
        // 初次连接的欢迎信息
    else if ( "welcome" == o["function"] ) {
        //writeToTop('<span style="color: blue;">your ip : '+ o['ip'] + '</span>');
    }
        // 如果有设备断开
    else if ( "deviceClosed" == o["function"] ) {
        var ip = o["ip"]
        e = $("span[ip='"+ip+"']")
        e.removeClass("deviceConnected")
        e.addClass("deviceClosed")
    }
        // 如果有新设备连接上来
    else if ( "deviceConnected" == o["function"] ) {
        var ip = o["ip"]
        e = $("span[ip='"+ip+"']")
        if ( e && 0 == e.length ){
            addDevice(o["ip"]);
        }
        else {
            e.removeClass("deviceClosed")
            e.addClass("deviceConnected")
        }
    }
    else{
        // writeToTop('<span style="color: gray;">'+ evt.data+'</span>');
    }
}
function onError(evt) {
    writeToTop('<span style="color: red;">ERROR:</span> '+ evt.data);
}
function doSend(message) {
    websocket.send(message);
}
// 更新顶部状态信息
function  writeToTop(message) {
    var pre = document.createElement("p");
    pre.style.wordWrap = "break-word";
    pre.innerHTML = message;
    t = $("#topDiv")
    t.html(pre)
}
// 写透传日志
function  writeToLog(message) {
    var pre = document.createElement("diva");
    pre.style.wordWrap = "break-word";
    pre.innerHTML = message;

    t = $("#outputDiv")
    t.append(pre)
    t.animate({scrollTop:t.prop('scrollHeight')});
}
var preClickElement = null
function layoutDevices(devies) {
    devies.forEach(function (u) {
        addDevice(u);
    })

     $("#devicesDiv > span:first").trigger("click")
}
// 增加设备
function addDevice(u) {
    deviesDiv = $("#devicesDiv")
    s = $("<span  ip="+ u+">" + u  + "</span>")
    s.addClass("deviceConnected")
    s.css("background-color","#ffffff")

    deviesDiv.append(s)
    s.click(clickDevice)
}

// 当点击设备按钮时
function clickDevice(e) {
    if( null != preClickElement ) {
        preClickElement.removeClass("touched")
        preClickElement.css("background-color","#ffffff")

    }
    $(this).addClass("touched")
    $(this).css("background-color","#eeeeee")

    t = $("#outputDiv")
    t.empty()
    writeToLog("<span style='color:lightgray' >start receive data from IP:" +  $(this).text() + "</span>")
    doSend("tail:" + $(this).text());
    preClickElement = $(this)
}


window.addEventListener("load", init, false);