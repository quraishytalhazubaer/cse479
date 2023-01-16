// Get the edit button and modal element
    const editBtn = document.querySelector('.edit-btn');
    const editModal = document.querySelector('#editModal');

    // Add an event listener to the edit button
    editBtn.addEventListener('click', function(e) {
      // Show the modal
      editModal.style.display = 'block';
    });