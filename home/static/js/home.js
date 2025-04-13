console.log('home.js loaded')
const dropZone = document.getElementById('dropZone')
  const formFile = document.getElementById('formFile')
  const errorMessage = document.getElementById('errorMessage')

  const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']
  const maxSize = 5 * 1024 * 1024 // 5MB

  function validateFile(file) {
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Invalid file type. Please upload JPEG, PNG or PDF files.')
    }
    if (file.size > maxSize) {
      throw new Error('File too large. Maximum size is 5MB.')
    }
  }

  function showError(message) {
    errorMessage.textContent = message
    errorMessage.classList.remove('d-none')
  }

  function hideError() {
    errorMessage.classList.add('d-none')
  }

  dropZone.addEventListener('click', () => formFile.click())

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault()
    dropZone.classList.add('bg-light')
  })

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('bg-light')
  })

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault()
    dropZone.classList.remove('bg-light')
    hideError()

    try {
      const file = e.dataTransfer.files[0]
      validateFile(file)
      formFile.files = e.dataTransfer.files
      updateDropZoneText()
    } catch (error) {
      showError(error.message)
    }
  })

  formFile.addEventListener('change', () => {
    hideError()
    try {
      if (formFile.files.length > 0) {
        validateFile(formFile.files[0])
        updateDropZoneText()
      }
    } catch (error) {
      showError(error.message)
      formFile.value = ''
    }
  })

  function updateDropZoneText() {
    dropZone.textContent =
      formFile.files.length > 0
        ? formFile.files[0].name
        : 'Drag and drop a file here or click to select'
  }

