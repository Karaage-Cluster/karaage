// load jquery and jquery-ui if needed
// into window.jQuery
if (typeof window.jQuery === 'undefined') {
  document.write('<script type="text/javascript"  src="../js/jquery.min.js"><\/script><script type="text/javascript"  src="../js/jquery-ui.js"><\/script><link type="text/css" rel="stylesheet" href="../css/jquery-ui.css" />');
} else if(typeof window.jQuery.ui === 'undefined' || typeof window.jQuery.ui.autocomplete === 'undefined') {
  document.write('<script type="text/javascript"  src="../jquery-ui.js"><\/script><link type="text/css" rel="stylesheet" href="../css/jquery-ui.css" />');
}

