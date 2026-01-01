document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData();
    const image = document.getElementById('imageInput').files[0];
    formData.append('image', image);

    const response = await fetch('/extract', {
        method: 'POST',
        body: formData
    });

    const text = await response.text();
    document.getElementById('output').textContent = text;

    function resetForm() {
  fileInput.value = '';
  fileName.textContent = '';
  document.getElementById('uploadForm').reset();
  
  // Optional: Clear extracted text section if present
  const textBox = document.querySelector('textarea');
  if (textBox) {
    textBox.value = '';
  }
}
function clearText() {
  document.getElementById("outputText").value = "";
}
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const imagePreview = document.getElementById('imagePreview');

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    fileName.textContent = "📎 " + file.name;

    // Show image preview
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      imagePreview.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
  }
});

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    fileInput.files = files;
    fileName.textContent = "📎 " + files[0].name;

    // Show image preview
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      imagePreview.classList.remove("hidden");
    };
    reader.readAsDataURL(files[0]);
  }
});



});
