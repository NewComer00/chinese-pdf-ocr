// Loaded via <script> tag, create shortcut to access PDF.js exports.
var pdfjsLib = window['pdfjs-dist/build/pdf'];

/**
 * TODO
 * pdf.js seems to automatically find my local pdf-xxx.worker.js
 * maybe we don't need to specify workerSrc manually?
 */
//pdfjsLib.GlobalWorkerOptions.workerSrc = ;

// the minimum displayed edge length of the PDF page
const SHORT_EDGE_MINLEN = 960;

// pdf rendering related settings
var pdfDoc = null,
    pageNum = 1,
    pageRendering = false,
    pageNumPending = null,
    scale = 1,
    pdfCanvas = document.getElementById('pdf-layer'),
    pdfCanvasCtx = pdfCanvas.getContext('2d'),
    ocrCanvas = new fabric.Canvas('ocr-layer');

// alert banner settings
var textCopiedAlert = new BootstrapAlert({
    dismissible: true,
    fadeIn: true,
    destroyAfter: 1500
});
textCopiedAlert.setBackground('success'); // set the alert to a success one
textCopiedAlert.addP('<b>📋✅ OCR text copied to clipboard.</b>');

/**
 * Get page info from document, resize canvas accordingly, and render page.
 * @param num Page number.
 */
function renderPage(num) {
    pageRendering = true;
    // Using promise to fetch the page
    pdfDoc.getPage(num).then(function(page) {
        // scale the page if too small
        var originalViewport = page.getViewport({scale: 1});
        if (originalViewport.width <= originalViewport.height) {
            scale = Math.max(
                SHORT_EDGE_MINLEN,
                document.getElementById("canvas-layers").offsetWidth
            ) / originalViewport.width;
        } else {
            scale = SHORT_EDGE_MINLEN / Math.min(
                SHORT_EDGE_MINLEN, originalViewport.height);
        }
        // scaling...
        var scaledViewport = page.getViewport({scale: scale});
        pdfCanvas.height = scaledViewport.height;
        pdfCanvas.width = scaledViewport.width;

        // Render PDF page into canvas context
        var renderContext = {
            canvasContext: pdfCanvasCtx,
            viewport: scaledViewport
        };
        var renderTask = page.render(renderContext);

        // Wait for rendering to finish
        renderTask.promise.then(function() {
            pageRendering = false;
            if (pageNumPending !== null) {
                // New page rendering is pending
                renderPage(pageNumPending);
                pageNumPending = null;
            }
        });
    });

    // Update page counters
    document.getElementById('page_num').textContent = num;
}

/**
 * If another page rendering in progress, waits until the rendering is
 * finised. Otherwise, executes rendering immediately.
 */
function queueRenderPage(num) {
    if (pageRendering) {
        pageNumPending = num;
    } else {
        renderPage(num);
    }
}

/**
 * Displays previous page.
 */
function onPrevPage() {
    if (pageNum <= 1) {
        return;
    }
    ocrCanvas.clear();
    pageNum--;
    queueRenderPage(pageNum);
    // scroll to top
    $('html,body').scrollTop(0);
}
document.getElementById('prev').addEventListener('click', onPrevPage);

/**
 * Displays next page.
 */
function onNextPage() {
    if (pageNum >= pdfDoc.numPages) {
        return;
    }
    ocrCanvas.clear();
    pageNum++;
    queueRenderPage(pageNum);
    // scroll to top
    $('html,body').scrollTop(0);
}
document.getElementById('next').addEventListener('click', onNextPage);

/**
 * Do OCR on this page.
 */
function onDoOcr() {
    if (pageNum < 1 || pageNum > pdfDoc.numPages) {
        return;
    }
    // send the current pdf canvas as an image to the python backend
    var pageImg = pdfCanvas.toDataURL('image/png')
    var jqXHR = $.ajax({
        type: "POST",
        url: "/",
        async: false,
        data: {
            page_img: pageImg
        }
    });
    var labeledTextbox = JSON.parse(jqXHR.responseText);

    // prepare the canvas
    ocrCanvas.setHeight(pdfCanvas.height);
    ocrCanvas.setWidth(pdfCanvas.width);
    ocrCanvas.clear();

    // setting the textboxes to be drawn...
    for (var [label, textbox] of Object.entries(labeledTextbox)) {
        var boundingBox = textbox[0]
        var rect = new fabric.Rect({
            left: boundingBox[0],
            top: boundingBox[1],
            width: boundingBox[2],
            height: boundingBox[3],
            fill: 'red',
            opacity: 0.3,
            lockMovementX: true,
            lockMovementY: true,
            lockScalingX: true,
            lockScalingY: true,
            lockRotation: true,
            hasControls: false,
            hoverCursor: 'pointer'
        });
        rect.text = textbox[1]; // add text field to rect obj

        // if we click the textbox, copy the ocr text to clipboard
        rect.on('mouseup', function() {
            navigator.clipboard.writeText(this.text);
            document.getElementById('alert-flex-container').appendChild(textCopiedAlert.render());
            // to correctly select the overlapped object
            ocrCanvas.discardActiveObject();
        });

        // draw the textbox on canvas
        ocrCanvas.add(rect);
    }
}
document.getElementById('do-ocr').addEventListener('click', onDoOcr);

/**
 * Asynchronously downloads PDF.
 */
document.getElementById('file').onchange = function(event) {
    var file = event.target.files[0];
    var fileReader = new FileReader();
    fileReader.onload = function() {
        var typedarray = new Uint8Array(this.result);

        var loadingTask = pdfjsLib.getDocument(typedarray);
        loadingTask.promise.then(function(pdf) {
            pdfDoc = pdf;
            document.getElementById('page_count').textContent = pdfDoc.numPages;

            // Initial/first page rendering
            renderPage(pageNum);
        });
    }
    fileReader.readAsArrayBuffer(file);
}

//plugin to make current page text editable
$.fn.extend({
    editable: function () {
        $(this).each(function () {
            var $el = $(this),
            $edittextbox = $('<input type="text"></input>').css('min-width', $el.width()),
            submitChanges = function () {
                if ($edittextbox.val() !== '') {
                    $el.html($edittextbox.val());
                    $el.show();
                    $el.trigger('editsubmit', [$el.html()]);
                    $(document).unbind('click', submitChanges);
                    $edittextbox.detach();
                }
            },
            tempVal;
            $edittextbox.click(function (event) {
                event.stopPropagation();
            });

            $el.dblclick(function (e) {
                tempVal = $el.html();
                $edittextbox.val(tempVal).insertBefore(this)
                .bind('keypress', function (e) {
                    var code = (e.keyCode ? e.keyCode : e.which);
                    if (code == 13) {
                        submitChanges();
                    }
                }).select();
                $el.hide();
                $(document).click(submitChanges);
            });
        });
        return this;
    }
});

// double click page number to change the current page
$('#page_num').editable().on('editsubmit', function (event, val) {
    var num = parseInt(val);
    // if input is legal...
    if (!isNaN(num) && num > 0 && num <= pdfDoc.numPages) {
        // only act when page number is really changed
        if (num != pageNum) {
            ocrCanvas.clear();
            pageNum = num;
            queueRenderPage(pageNum);
            $('html,body').scrollTop(0);
        }
    } else {
        // if illegal, keep the page number unchanged
        document.getElementById('page_num').textContent = pageNum;
    }
});
