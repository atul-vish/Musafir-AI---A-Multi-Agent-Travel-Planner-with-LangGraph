let currentThreadId = localStorage.getItem("travel_thread_id") || null;
let latestAnswerMarkdown = "";

function setPrompt(text) {
    document.getElementById("userInput").value = text;
}

function setLoading(isLoading) {
    const sendBtn = document.getElementById("sendBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    sendBtn.disabled = isLoading;

    if (isLoading) {
        btnText.classList.add("hidden");
        btnLoader.classList.remove("hidden");
    } else {
        btnText.classList.remove("hidden");
        btnLoader.classList.add("hidden");
    }
}

function showError(message) {
    const errorBox = document.getElementById("errorBox");

    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function hideError() {
    const errorBox = document.getElementById("errorBox");

    errorBox.classList.add("hidden");
    errorBox.textContent = "";
}

function showResult(answer, threadId) {
    latestAnswerMarkdown = answer;

    const resultSection = document.getElementById("resultSection");
    const resultBox = document.getElementById("resultBox");
    const threadInfo = document.getElementById("threadInfo");

    if (typeof marked !== "undefined") {
        resultBox.innerHTML = marked.parse(answer);
    } else {
        resultBox.innerText = answer;
    }

    threadInfo.textContent = `Thread ID: ${threadId}`;

    resultSection.classList.remove("hidden");

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

async function sendMessage() {
    hideError();

    const input = document.getElementById("userInput");
    const message = input.value.trim();

    if (!message) {
        showError("Please enter your travel request first.");
        return;
    }

    setLoading(true);

    try {
        const response = await fetch("/api/travel", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                thread_id: currentThreadId
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Something went wrong.");
        }

        currentThreadId = data.thread_id;
        localStorage.setItem("travel_thread_id", currentThreadId);

        showResult(data.answer, data.thread_id);

    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

function copyResult() {
    const resultBox = document.getElementById("resultBox");
    const text = resultBox.innerText;

    if (!text) {
        return;
    }

    navigator.clipboard.writeText(text)
        .then(() => {
            const copyBtn = document.querySelector(".copy-btn");
            const oldText = copyBtn.textContent;

            copyBtn.textContent = "Copied!";

            setTimeout(() => {
                copyBtn.textContent = oldText;
            }, 1400);
        })
        .catch(() => {
            showError("Could not copy result.");
        });
}

function downloadPDF() {
    const pdfContent = document.getElementById("pdfContent");

    if (!latestAnswerMarkdown || !pdfContent) {
        showError("No travel plan available to download.");
        return;
    }

    const downloadBtn = document.querySelector(".download-btn");
    const oldText = downloadBtn.textContent;

    downloadBtn.textContent = "Preparing PDF...";
    downloadBtn.disabled = true;

    // Render a clean copy of the plan in an off-screen, fixed-width sandbox.
    // Capturing the live element makes html2canvas include the page's scroll
    // offset and the hero/card layout above it, which shows up as a large
    // blank band at the top of the PDF.
    const PDF_WIDTH_PX = 794; // A4 width at 96 dpi

    const sandbox = document.createElement("div");
    sandbox.style.cssText = [
        "position: fixed",
        "top: 0",
        "left: 0",
        `width: ${PDF_WIDTH_PX}px`,
        "z-index: -1",
        "background: #ffffff",
        "pointer-events: none"
    ].join(";");

    const clone = pdfContent.cloneNode(true);
    clone.removeAttribute("id");
    clone.style.cssText = [
        "margin: 0",
        "padding: 0",
        "border: none",
        "box-shadow: none",
        `width: ${PDF_WIDTH_PX}px`,
        "background: #ffffff"
    ].join(";");

    // Show the title that is hidden on screen, and drop anything that is UI-only.
    const pdfTitle = clone.querySelector(".pdf-title");
    if (pdfTitle) {
        pdfTitle.style.display = "block";
        pdfTitle.style.marginTop = "0";
    }
    clone.querySelectorAll(".result-actions, #threadInfo").forEach(el => el.remove());

    // Make sure nothing at the top of the document adds spacing.
    const firstChild = clone.firstElementChild;
    if (firstChild) {
        firstChild.style.marginTop = "0";
        firstChild.style.paddingTop = "0";
    }

    sandbox.appendChild(clone);
    document.body.appendChild(sandbox);

    const options = {
        margin: [0.5, 0.5, 0.6, 0.5], // top, left, bottom, right (inches)
        filename: "ai-travel-plan.pdf",
        image: {
            type: "jpeg",
            quality: 0.98
        },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: "#ffffff",
            scrollX: 0,
            scrollY: 0,
            x: 0,
            y: 0,
            windowWidth: PDF_WIDTH_PX
        },
        jsPDF: {
            unit: "in",
            format: "a4",
            orientation: "portrait"
        },
        // "avoid-all" pushed every table/list to the next page and left big
        // empty gaps. Only keep rows and headings from splitting instead.
        pagebreak: {
            mode: ["css", "legacy"],
            avoid: ["tr", "h1", "h2", "h3", "li"]
        }
    };

    const cleanup = () => {
        sandbox.remove();
        downloadBtn.textContent = oldText;
        downloadBtn.disabled = false;
    };

    html2pdf()
        .set(options)
        .from(clone)
        .save()
        .then(cleanup)
        .catch(() => {
            cleanup();
            showError("Could not download PDF.");
        });
}

document.addEventListener("keydown", function(event) {
    if (event.ctrlKey && event.key === "Enter") {
        sendMessage();
    }
});