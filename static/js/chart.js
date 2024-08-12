document.addEventListener("DOMContentLoaded", function() {
    // Chart Options
    const getChartOptions = (chartLabel) => {
        return {
            series: [30, 25], // Default values
            colors: ["#16BDCA", "#FDBA8C", "#007D86"],
            chart: {
                height: 320,
                width: "100%",
                type: "donut",
            },
            stroke: {
                colors: ["transparent"],
            },
            plotOptions: {
                pie: {
                    donut: {
                        labels: {
                            show: true,
                            name: {
                                show: true,
                                fontFamily: "Inter, sans-serif",
                                offsetY: 20,
                            },
                            total: {
                                showAlways: true,
                                show: true,
                                label: chartLabel,
                                fontFamily: "Inter, sans-serif",
                                formatter: function (w) {
                                    const sum = w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                                    return sum;
                                },
                            },
                            value: {
                                show: true,
                                fontFamily: "Inter, sans-serif",
                                offsetY: -20,
                                formatter: function (value) {
                                    return value;
                                },
                            },
                        },
                        size: "80%",
                    },
                },
            },
            grid: {
                padding: {
                    top: -2,
                },
            },
            labels: ["Ai", "Not Ai"],
            dataLabels: {
                enabled: false,
            },
            legend: {
                position: "bottom",
                fontFamily: "Inter, sans-serif",
            },
        };
    };

    // Render Chart Function
    const renderChart = (chartId, chartLabel) => {
        if (document.getElementById(chartId) && typeof ApexCharts !== 'undefined') {
            const chart = new ApexCharts(document.getElementById(chartId), getChartOptions(chartLabel));
            chart.render();

            if (chartId === "donut-chart-1") {
                document.getElementById('check-ai-button').addEventListener('click', async () => {
                    const fileInput = document.getElementById('dropzone-file');
                    const fileType = document.querySelector('input[name="file-type"]:checked').value;
                
                    const file = fileInput.files[0];
                    if (!file) {
                        console.error('No file selected');
                        return;
                    }
                
                    const formData = new FormData();
                    formData.append('file', file);
                    formData.append('file_type', fileType);
                
                    try {
                        const response = await fetch('/handle_file_upload/', {
                            method: 'POST',
                            body: formData,
                        });
                    
                        // Check if the response is in JSON format
                        const contentType = response.headers.get('Content-Type');
                        if (!contentType || !contentType.includes('application/json')) {
                            const text = await response.text(); // Read response as text
                            console.error('Unexpected response format:', text);
                            return;
                        }
                    
                        const data = await response.json();
                        if (response.ok) {
                            // Update chart with the confidence levels from server response
                            console.log('Response data:', data);
                            const { confidence } = data;
                            chart.updateSeries(confidence);
                        } else {
                            console.error('Server error:', data.error);
                        }
                    } catch (error) {
                        console.error('Error uploading file:', error);
                    }
                    
                });
                
            } else if (chartId === "donut-chart-2") {
                document.getElementById('update-chart-button').addEventListener('click', () => {
                    const checkboxes = document.querySelectorAll('#devices-2 input[type="checkbox"]');
                    let imageCount = 0;
                    let videoCount = 0;
                    let audioCount = 0;

                    checkboxes.forEach((checkbox) => {
                        if (checkbox.checked) {
                            switch (checkbox.value) {
                                case 'image':
                                    imageCount++;
                                    break;
                                case 'video':
                                    videoCount++;
                                    break;
                                case 'audio':
                                    audioCount++;
                                    break;
                            }
                        }
                    });

                    const updatedSeries = [imageCount, videoCount, audioCount];
                    chart.updateSeries(updatedSeries);
                });
            }
        }
    };

    // Render Both Charts
    // renderChart("donut-chart-1", "Model Confidence");
    renderChart("donut-chart-2");

    // File Input Handling
    const dropdownButton = document.getElementById('dropdownRadioBgHoverButton');
    const dropdownMenu = document.getElementById('dropdownRadioBgHover');
    const fileInput = document.getElementById('dropzone-file');
    const uploadText = document.getElementById('file-upload-text');

    // Toggle Dropdown Menu Visibility
    dropdownButton.addEventListener('click', function () {
        dropdownMenu.classList.toggle('hidden');
    });

    // Update File Input Type and Placeholder Text
    dropdownMenu.addEventListener('change', function (e) {
        if (e.target.name === 'file-type') {
            const type = e.target.value;
            let buttonText = 'Dropdown radio';
            switch (type) {
                case 'image':
                    fileInput.accept = 'image/*';
                    uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop (SVG, PNG, JPG or GIF, MAX. 800x400px)';
                    buttonText = 'Selected: Image';
                    break;
                case 'video':
                    fileInput.accept = 'video/*';
                    uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop (Video files only)';
                    buttonText = 'Selected: Video';
                    break;
                case 'audio':
                    fileInput.accept = 'audio/*';
                    uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop (Audio files only)';
                    buttonText = 'Selected: Audio';
                    break;
                default:
                    fileInput.accept = '';
                    uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop';
                    buttonText = 'Dropdown radio';
            }
            console.log(`File type set to: ${type}`);
            // Update Button Text
            dropdownButton.innerHTML = `${buttonText}
               <svg class="w-2.5 h-2.5 ms-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
                   <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
               </svg>`;
            // Hide Dropdown Menu After Selection
            dropdownMenu.classList.add('hidden');
        }
    });
    

    // Close Dropdown Menu When Clicking Outside
    document.addEventListener('click', function (e) {
        if (!dropdownButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
            dropdownMenu.classList.add('hidden');
        }
    });

    // Handle File Input Change Event
    fileInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            // Update the Placeholder Text
            uploadText.innerHTML = `<span class="font-semibold">File selected:</span> ${file.name}`;
            
            // Display File Preview Based on File Type
            const filePreviewDiv = document.getElementById('file-preview');
            filePreviewDiv.innerHTML = ''; // Clear Previous Content

            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.classList.add('w-full', 'h-auto', 'mt-4');
                    filePreviewDiv.appendChild(img);
                };
                reader.readAsDataURL(file);
            } else if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.src = URL.createObjectURL(file);
                video.controls = true;
                video.classList.add('w-full', 'h-auto', 'mt-4');
                filePreviewDiv.appendChild(video);
            } else if (file.type.startsWith('audio/')) {
                const audio = document.createElement('audio');
                audio.src = URL.createObjectURL(file);
                audio.controls = true;
                audio.classList.add('w-full', 'mt-4');
                filePreviewDiv.appendChild(audio);
            } else {
                // Handle Other File Types or Clear Content
                filePreviewDiv.innerHTML = '<p class="text-red-500">Unsupported file type</p>';
            }
        } else {            // No File Selected, Revert to Default Text
            uploadText.innerHTML = '<span class="font-semibold">Click to upload</span> or drag and drop';
            // Clear Any Previous Previews
            const filePreviewDiv = document.getElementById('file-preview');
            filePreviewDiv.innerHTML = '';
        }
    });
});
