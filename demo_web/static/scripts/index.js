// Loaded via <script> tag, create shortcut to access PDF.js exports.
var pdfjsLib = window['pdfjs-dist/build/pdf'];

// The workerSrc property shall be specified.
pdfjsLib.GlobalWorkerOptions.workerSrc = '//mozilla.github.io/pdf.js/build/pdf.worker.js';

// the minimum displayed edge length of the PDF page
const SHORT_EDGE_MINLEN = 960;

var pdfDoc = null,
    pageNum = 1,
    pageRendering = false,
    pageNumPending = null
    scale = 1,
    canvas = document.getElementById('the-canvas'),
    ctx = canvas.getContext('2d'),
    ocrCanvas = new fabric.Canvas('ocr-layer');

/**
 * Get page info from document, resize canvas accordingly, and render page.
 * @param num Page number.
 */
function renderPage(num) {
  pageRendering = true;
  // Using promise to fetch the page
  pdfDoc.getPage(num).then(function(page) {
    // scale the page if too small
    var original_page_width = page.getViewport({scale: 1}).width;
    var original_page_height = page.getViewport({scale: 1}).height;
    if (original_page_width <= original_page_height) {
      scale = Math.max(
        SHORT_EDGE_MINLEN,
        document.getElementById("canvas-layers").offsetWidth
        ) / original_page_width;
    } else {
      scale = SHORT_EDGE_MINLEN / Math.min(
        SHORT_EDGE_MINLEN, original_page_height);
    }
    var viewport = page.getViewport({scale: scale});
    canvas.height = viewport.height;
    canvas.width = viewport.width;

    // Render PDF page into canvas context
    var renderContext = {
      canvasContext: ctx,
      viewport: viewport
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
}
document.getElementById('next').addEventListener('click', onNextPage);

/**
 * Do OCR on this page.
 */
function onDoOcr() {
  if (pageNum < 1 || pageNum > pdfDoc.numPages) {
    return;
  }
  var pageImg = canvas.toDataURL('image/png')
  var jqXHR = $.ajax({
    type: "POST",
    url: "/",
    async: false,
    data: { page_img: pageImg }
  });
  var labeledTextbox = JSON.parse(jqXHR.responseText);

  ocrCanvas.setHeight(canvas.height);
  ocrCanvas.setWidth(canvas.width);
  ocrCanvas.clear();

  var rectList = [];
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
    // add text field to rect obj
    rect.text = textbox[1];
    rectList.push(rect);
  }

  for (var r of rectList) {
    r.on('mouseup', function() {
      navigator.clipboard.writeText(this.text);
      document.getElementById('alert-flex-container').appendChild(textCopiedAlert.render());
      // to correctly select the overlapped object
      ocrCanvas.discardActiveObject();
    });
  }
  ocrCanvas.add(...rectList);
}
document.getElementById('do-ocr').addEventListener('click', onDoOcr);
var textCopiedAlert = new BootstrapAlert({
  dismissible: true,
  fadeIn: true,
  destroyAfter: 1500
  });
textCopiedAlert.setBackground('success'); // set the alert to a success one
textCopiedAlert.addP('<b>📋✅ OCR text copied to clipboard.</b>');

/**
 * Asynchronously downloads PDF.
 */
document.getElementById('file').onchange = function(event) {
  var file = event.target.files[0];
  var fileReader = new FileReader();
  fileReader.onload = function() {
    var typedarray = new Uint8Array(this.result);
    console.log(typedarray);

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
