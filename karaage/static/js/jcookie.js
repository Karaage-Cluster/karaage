/**
 *
 * jCookie - https://github.com/martinkr/jCookie
 *
 * jCookie - a jQuery-Plugin providing an convenient api for CRUD-related cookie handling.
 *
 * @version 1.2.0
 *
 * @example:
 *  Create,update:
 *    jQuery.jCookie('cookie','value');
 *  Delete:
 *    jQuery.jCookie('cookie',null);
 *  Read:
 *    jQuery.jCookie('cookie');
 *
 * Copyright (c) 2008-2011 Martin Krause (jquery.public.mkrause.info)
 * Dual licensed under the MIT and GPL licenses.
 *
 * @author Martin Krause public@mkrause.info
 * @copyright Martin Krause (jquery.public.mkrause.info)
 * @license MIT http://www.opensource.org/licenses/mit-license.php
 * @license GNU http://www.gnu.org/licenses/gpl-3.0.html
 *
 * @requires
 *  jQuery JavaScript Library - http://jquery.com/
 *    Copyright 2010, John Resig
 *    Dual licensed under the MIT or GPL Version 2 licenses - http://jquery.org/license
 *
 */

// JSLint setting, @see http://www.jslint.com/lint.html#options
/*jslint devel: false, browser: true, continue: true, eqeq: true, vars: true, evil: true, white: true, forin: true, css: true, cap: true, nomen: true, plusplus: true, maxerr: 500, indent: 4 */


/**
 *
 * @param {String} sCookieName_, the cookie name
 * @param {Object} [oValue_], the cokie value
 * @param {String, Number} [oExpires_], the expire date as string ('session') or number
 * @param {Object} [oOptions_], additional cookie options { path: {String}, domain: {String}, secure {Bool} }
 */
jQuery.jCookie = function(sCookieName_, oValue_, oExpires_, oOptions_) {

	// cookies disabled
	if (!navigator.cookieEnabled) { return false; }

	// enfoce params, even if just an object has been passed
	var oOptions_ = oOptions_ || {};
	if (typeof(arguments[0]) !== 'string' && arguments.length === 1) {
		oOptions_ = arguments[0];
		sCookieName_ = oOptions_.name;
		oValue_ = oOptions_.value;
		oExpires_ = oOptions_.expires;
	}

	// escape characters
	sCookieName_ = encodeURI(sCookieName_);

	// basic error handling
	if (oValue_ && (typeof(oValue_) !== 'number' && typeof(oValue_) !== 'string' && oValue_ !== null)) { return false; }

	// force values
	var _sPath = oOptions_.path ? "; path=" + oOptions_.path : "";
	var _sDomain = oOptions_.domain ? "; domain=" + oOptions_.domain : "";
	var _sSecure = oOptions_.secure ? "; secure" : "";
	var sExpires_ = "";

	// write ('n delete ) cookie even in case the value === null
	if (oValue_ || (oValue_ === null && arguments.length == 2)) {

		// set preceding expire date in case: expires === null, or the arguments have been (STRING,NULL)
		oExpires_ = (oExpires_ === null || (oValue_ === null && arguments.length == 2)) ? -1 : oExpires_;

		// calculate date in case it's no session cookie (expires missing or expires equals 'session' )
		if (typeof(oExpires_) === 'number' && oExpires_ != 'session' && oExpires_ !== undefined) {
			var _date = new Date();
			_date.setTime(_date.getTime() + (oExpires_ * 24 * 60 * 60 * 1000));
			sExpires_ = ["; expires=", _date.toGMTString()].join("");
		}
		// write cookie
		document.cookie = [sCookieName_, "=", encodeURI(oValue_), sExpires_, _sDomain, _sPath, _sSecure].join("");

		return true;
	}

	// read cookie
	if (!oValue_ && typeof(arguments[0]) === 'string' && arguments.length == 1 && document.cookie && document.cookie.length) {
		// get the single cookies
		var _aCookies = document.cookie.split(';');
		var _iLenght = _aCookies.length;
		// parse cookies
		while (_iLenght--) {
			var _aCurrrent = _aCookies[_iLenght].split("=");
			// find the requested one
			if (jQuery.trim(_aCurrrent[0]) === sCookieName_) { return decodeURI(_aCurrrent[1]); }
		}
		return undefined;
	}
	// no cookie present
	if(!document.cookie || !document.cookie.length) { return undefined;}

	return false;
};
