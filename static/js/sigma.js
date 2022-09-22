/*
https://stackoverflow.com/a/44547866
 */
window.addEventListener('load', () => {
    if(window.self === window.top) // if w.self === w.top, we are not in an iframe
        return;

    send_height_to_parent_function = function(){
        var height = $(document).height();
        //console.log("Sending height as " + height + "px");
        parent.postMessage({'height' : height }, '*');
    }

    // send message to parent about height updates
    send_height_to_parent_function(); //whenever the page is loaded
    window.addEventListener('resize', send_height_to_parent_function); // whenever the page is resized
    var observer = new MutationObserver(send_height_to_parent_function);           // whenever DOM changes PT1
    var config = { attributes: true, childList: true, characterData: true, subtree:true}; // PT2
    observer.observe(window.document, config);                                            // PT3 
});