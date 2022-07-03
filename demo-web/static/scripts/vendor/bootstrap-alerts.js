/**
 * Works in the same way as setTimeout, except this has a callback as a third option.
 * @param  {Function} func     A function to call after a specified delay.
 * @param  {integer}  time     The delay, in milliseconds.
 * @param  {Function} callback The callback function.
 */
function customTimeout(func, time, callback) {
    setTimeout(function() {
        func();
        if (typeof callback != "undefined") {
            callback();
        }
    }, time);
}

// https://stackoverflow.com/a/11197343/3578036
function extend() {
    for (var i = 1; i < arguments.length; i++)
        for (var key in arguments[i])
            if (arguments[i].hasOwnProperty(key))
                arguments[0][key] = arguments[i][key];
    return arguments[0];
}

// https://stackoverflow.com/q/1744310/3578036
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function(obj, start) {
        for (var i = (start || 0), j = this.length; i < j; i++) {
            if (this[i] === obj) { return i; }
        }
        return -1;
    }
}

if (!Element.prototype.hasClass) {
    Element.prototype.hasClass = function(classname) {
        return (this.className && new RegExp("(^|\\s)" + classname + "(\\s|$)").test(this.className)) || false;
    };
}

if (!Element.prototype.addClass) {
    Element.prototype.addClass = function (classname) {
        if (this.hasClass(classname) || classname == undefined) {
            return this;
        }
        
        this.className += (this.className.length <= 0 ? "" : " ") + classname;
        return this;
    };
}

/**
 * Dynamically create Bootstrap alerts during runtime.
 * @param {object} options The various properties are listed below:
 *                         - dismissible: Boolean
 *                           When you want to have a dismissible alert, then set
 *                           this to true.
 *                         - fadeIn: Boolean
 *                           This option requires CSS3 animations and also an
 *                           animation to be created; see below
 *                           @keyframes alertFadeIn { from { opacity: 0; } to { opacity: 1; } }
 *                           .alert.fade.show {animation: alertFadeIn 0.4s;}
 *                         - destroyAfter: integer
 *                           A number, in milliseconds, after which the alert
 *                           will be deleted from the DOM. This also uses jQuery
 *                           fadeOut(400) to make the appearance of a smooth
 *                           deletion. Set to 0 or below to disable this option.
 *                           By default it is set to 3000, but will only work if
 *                           dismissible is set to true.
 *                         - max: integer
 *                           A natural number that specifies the amount of alerts
 *                           that can be created. If setting this _you must_
 *                           also set maxId to a value so that the JS can
 *                           determine how many of that element have already been
 *                           created. Set to 0 or below to disable, or don't set maxId
 *                         - maxId: string
 *                           Any string that you want, provided it is shorter than
 *                           the ECMAScript limit. However that is high, very high.
 *                           Currently, the highest alert is deleted. That is,
 *                           the alert that is closest to the <head> element will
 *                           be removed first.
 *                         - background: string or integer
 *                           If a string is sent, it will be checked against the
 *                           valid alert backgrounds. The background must be
 *                           written without the "alert-" prefix.
 *                           If an integer is sent, it will be checked as an
 *                           array index against backgrounds array.
 *                           In both cases, if the background is invalid, primary
 *                           is used as a default.
 *                         - classes: string or array
 *                           In the case of a string, simply write the classes
 *                           as a space delimited string.
 *                           If an array, simply write each class as a new element.
 */
function BootstrapAlert(options) {
    options = typeof options == "undefined" ? {} : options;

    // default options
    let defaults = {
        dismissible: false, // whether the alert can be dismissed
        fadeIn: true, // this will cause the alert to fade in; requires CSS3 animations
        destroyAfter: 3000, // destory the alert after x milliseconds; 0 or below to prevent deleting
        max: 0, // the maximum number of alerts that can exist; 0 or below to ignore this setting
        maxId: "my-alert", // an indentifier to ensure only 'like' alerts are removed
        background: 'primary', // the default background colour
        classes: '' // any extra classes to include on the .alert
    };
    options = extend(defaults, options); // overwrite the defaults with the specified options
    
    let content = ''; // create the content functions

    this.isEmpty = function() {
        return content == '';
    }

    this.clear = function() {
        content = '';
        return this;
    }

    this.setBackground = function(bg) {
        // check that background is a valid one
        let validBgs = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'];

        // if it is a number, then use the index on the above array; otherwise check if is in the above array
        if (Number.isInteger(bg) && bg >= 1 && bg <= validBgs.length) {
            bg = validBgs[bg - 1];
        } else {
            bg = validBgs.indexOf(bg) > -1 ? bg : defaults.background;
        }

        // finally, initialise it to the options.background
        options.background = bg;

        // chaining, yo!
        return this;
    }
    this.setBg = this.setBackground;
    this.setBackground(options.background); // use this to also validate


    /** Use this to overwrite the content to just an HTML string. */
    this.setHTML = function(str) {
        content = str;

        return this;
    }

    /** Use this to add some HTML to the content. */
    this.addHTML = function(str) {
        content += str;

        return this;
    }

    /** Add a paragraph to the content. */
    this.addParagraph = function(str, classes) {
        classes = typeof classes == "undefined" ? "" : classes;

        content += '<p class="'+classes+'">'+str+'</p>';

        return this;
    }
    this.addP = this.addParagraph;

    /** Add an anchor to the content. */
    this.addLink = function(href, text, classes, target, title) {
        str = '<a href="'+href+'"';

        if (typeof text == "undefined") text = href;
        
        if (typeof classes != 'undefined') str += ' class="alert-link '+classes+'"';
        else str += 'class="alert-link"';
        
        if (typeof target != 'undefined') str += ' target="'+target+'"';
        if (typeof title != 'undefined') str += ' title="'+title+'"';
        str += '>'+text+'</a>';

        content += str;

        return this;
    }
    this.addA = this.addLink;

    /** Works the same as addLink(), except this will wrap the anchor in a <p> tag. */
    this.addParaLink = function(href, text, classes, target, title) {
        content += '<p>';
        this.addLink(href, text, classes, target, title); // reduce code by using this
        content += '</p>';

        return this;
    }
    this.addPA = this.addParaLink;

    /** Create a heading tag of a specified level. */
    this.addHeading = function(level, str, classes) {
        // only allow between 1 and 6 for the level
        if (level < 1)  level = 1;
        else if (level > 6) level = 6;
        // ensure it is a number; else default to level 1
        if (!Number.isInteger(level)) level = 1;

        content += '<h'+level+' class="alert-heading '+classes+'">'+str+'</h'+level+'>';

        return this;
    }
    this.addH = this.addHeading;


    
    // render the final result
    this.render = function() {
        // set the class for the alert
        let classes = 'alert alert-'+options.background;
        
        if (options.dismissible) classes += ' alert-dismissible';
        
        if (options.classes != '' || typeof options.classes != 'undefined') {
            if (typeof options.classes == "string") {
                classes += ' ' + options.classes;
            } else if (options.classes instanceof Array) {
                for (var i = 0; i < options.classes.length; i++) {
                    classes += ' ' + options.classes[i];
                }
            } else if (options.classes instanceof Object) {
                for (var cls in options.classes) {
                    classes += ' ' + cls;
                }
            }
        }

        // generate a random ID for this alert
        let id = "";
        let possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (var i = 0; i < 8; i++) id += possible.charAt(Math.floor(Math.random() * possible.length));
        
        if (options.fadeIn) {
            classes += ' fade';
            
            // time out just to give the element time to appear on the page and then fade it in
            setTimeout(function() {
                document.getElementById(id).addClass('show');
            }, 100);
        }
        
        // basics that all alerts have
        let html = '<div id="'+id+'" class="'+classes+'" role="alert"';
        
        // set up the max destroyer for alerts
        if (options.max > 0/* && options.maxId != ''*/) {
            html += ' data-max-id="'+options.maxId+'" data-max-count="'+options.max+'"';
            
            // if there are too many of that alert ID existing then delete one
            // the chosen one to delete is the one at the highest point in the DOM
            // meaning the closest one to the <head> element
            // ideally, this would be the 'oldest' created element
            let collection = document.getElementsByClassName('alert');
            let collectionCounts = 0;
            for (let i = 0; i < collection.length; i++) {
                if (collection[i].dataset.maxId) {
                    collectionCounts++;
                }
            }

            if (collectionCounts > options.maxId) {
                collection[0].parentNode.removeChild(collection[0]);
            }
        }

        html += '>'; // finish off with the closing angled bracket

        // self explanatory if statement
        if (options.dismissible) {
            html += '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'
                 +      '<span aria-hidden="true">&times;</span>'
                 +  '</button>';
        }

        html += content;
        html += '</div>';

        // create a timeout to destroy the alert
        if (options.dismissible && options.destroyAfter > 0) {
            customTimeout(function() {
                // fade the element out using the CSS transition
                document.getElementById(id).className = document.getElementById(id).className.replace(/\bshow\b/i, '');
            },
            options.destroyAfter,
            function() {
                // remove the element from the DOM after the CSS transistion is complete
                setTimeout(function() {
                    document.getElementById(id).parentNode.removeChild(document.getElementById(id));
                }, 400);
            });
        }
        
        // parse the HTML string
        let el = document.createElement('div');
        el.innerHTML = html;
        el = el.children[0]; // remove the parent node, extracting the alert only

        return el;
    }
}
