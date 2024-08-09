// console.log('inputfile.js is loaded');

// document.addEventListener('DOMContentLoaded', function () {
//     const dropdownButton = document.getElementById('dropdownRadioBgHoverButton');
//     const dropdownMenu = document.getElementById('dropdownRadioBgHover');
//     const fileInput = document.getElementById('dropzone-file');
//     const uploadText = document.getElementById('file-upload-text');

//     // Toggle dropdown menu visibility
//     dropdownButton.addEventListener('click', function () {
//         dropdownMenu.classList.toggle('hidden');
//     });

//     // Update file input type and placeholder text based on selected dropdown option
//     dropdownMenu.addEventListener('change', function (e) {
//         if (e.target.name === 'file-type') {
//             const type = e.target.value;
//             let buttonText = 'Dropdown radio';
//             switch (type) {
//                 case 'image':
//                     fileInput.accept = 'image/*';
//                     uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop (SVG, PNG, JPG or GIF, MAX. 800x400px)';
//                     buttonText = 'Selected: Image';
//                     break;
//                 case 'video':
//                     fileInput.accept = 'video/*';
//                     uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop (Video files only)';
//                     buttonText = 'Selected: Video';
//                     break;
//                 case 'audio':
//                     fileInput.accept = 'audio/*';
//                     uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop (Audio files only)';
//                     buttonText = 'Selected: Audio';
//                     break;
//                 default:
//                     fileInput.accept = '';
//                     uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop';
//                     buttonText = 'Dropdown radio';
//             }
//             // Update button text
//             dropdownButton.innerHTML = `${buttonText}
//                <svg class="w-2.5 h-2.5 ms-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
//                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
//                </svg>`;
//             // Hide dropdown menu after selection
//             dropdownMenu.classList.add('hidden');
//         }
//     });

//     // Close dropdown menu when clicking outside
//     document.addEventListener('click', function (e) {
//         if (!dropdownButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
//             dropdownMenu.classList.add('hidden');
//         }
//     });

//     // Handle file input change event
//     fileInput.addEventListener('change', function (e) {
//         const file = e.target.files[0];
//         if (file) {
//             // Update the placeholder text
//             uploadText.innerHTML = `<span class="font-semibold">File selected:</span> ${file.name}`;
            
//             // Display file preview based on file type
//             const filePreviewDiv = document.getElementById('file-preview');
//             filePreviewDiv.innerHTML = ''; // Clear previous content

//             if (file.type.startsWith('image/')) {
//                 const reader = new FileReader();
//                 reader.onload = function (e) {
//                     const img = document.createElement('img');
//                     img.src = e.target.result;
//                     img.classList.add('w-full', 'h-auto', 'mt-4');
//                     filePreviewDiv.appendChild(img);
//                 };
//                 reader.readAsDataURL(file);
//             } else if (file.type.startsWith('video/')) {
//                 const video = document.createElement('video');
//                 video.src = URL.createObjectURL(file);
//                 video.controls = true;
//                 video.classList.add('w-full', 'h-auto', 'mt-4');
//                 filePreviewDiv.appendChild(video);
//             } else if (file.type.startsWith('audio/')) {
//                 const audio = document.createElement('audio');
//                 audio.src = URL.createObjectURL(file);
//                 audio.controls = true;
//                 audio.classList.add('w-full', 'mt-4');
//                 filePreviewDiv.appendChild(audio);
//             } else {
//                 // Handle other file types or clear content
//                 filePreviewDiv.innerHTML = '<p class="text-red-500">Unsupported file type</p>';
//             }
//         } else {
//             // No file selected, revert to default text
//             uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop';
//             // Clear any previous previews
//             const filePreviewDiv = document.getElementById('file-preview');
//             filePreviewDiv.innerHTML = '';
//         }
//     });
// });
