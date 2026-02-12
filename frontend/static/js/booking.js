// Booking Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const serviceSelect = document.getElementById('service_id');
    const staffSelect = document.getElementById('staff_id');
    const scheduleSelect = document.getElementById('schedule_id');
    const bookingSummary = document.getElementById('booking-summary');
    const submitBtn = document.getElementById('submitBtn');
    const staffLoader = document.getElementById('staff-loader');
    const scheduleLoader = document.getElementById('schedule-loader');
    
    let selectedData = {
        service: null,
        staff: null,
        schedule: null
    };
    
    // Check if service ID is passed in URL and auto-select it
    function getURLParameter(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }
    
    // Update progress steps
    function updateSteps(activeStep) {
        for (let i = 1; i <= 4; i++) {
            const step = document.getElementById(`step-${i}`);
            if (i <= activeStep) {
                step.classList.add('active');
                if (i < activeStep) {
                    step.classList.add('completed');
                }
            } else {
                step.classList.remove('active', 'completed');
            }
        }
    }
    
    // Load staff when service is selected
    if (serviceSelect) {
        serviceSelect.addEventListener('change', async function() {
            const serviceId = this.value;
            
            if (!serviceId) {
                staffSelect.innerHTML = '<option value="">Select staff</option>';
                staffSelect.disabled = true;
                scheduleSelect.innerHTML = '<option value="">Select date & time</option>';
                scheduleSelect.disabled = true;
                selectedData.service = null;
                updateSummary();
                updateSteps(1);
                submitBtn.disabled = true;
                return;
            }
            
            // Store selected service data
            const selectedOption = this.options[this.selectedIndex];
            selectedData.service = {
                id: serviceId,
                name: selectedOption.text.split(' - ')[0],
                price: selectedOption.dataset.price,
                duration: selectedOption.dataset.duration,
                description: selectedOption.dataset.description
            };
            
            updateSteps(2);
            updateSummary();
            
            // Show loader
            staffLoader.style.display = 'block';
            staffSelect.style.display = 'none';
            
            // Load staff for selected service
            try {
                const response = await fetch(`/api/staff/?service_id=${serviceId}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const staff = await response.json();
                
                staffSelect.innerHTML = '<option value="">Select a staff member...</option>';
                
                if (staff.length === 0) {
                    staffSelect.innerHTML = '<option value="">⚠️ No staff available for this service</option>';
                    staffSelect.disabled = true;
                    
                    // Show helpful message
                    const helpMsg = document.createElement('div');
                    helpMsg.className = 'alert alert-warning mt-2';
                    helpMsg.innerHTML = '<i class="fas fa-exclamation-triangle"></i> No staff members are assigned to provide this service. Please contact the salon.';
                    staffSelect.parentElement.appendChild(helpMsg);
                    setTimeout(() => helpMsg.remove(), 5000);
                } else {
                    staff.forEach(member => {
                        const option = document.createElement('option');
                        option.value = member.id;
                        option.dataset.specialization = member.specialization;
                        option.dataset.name = member.user.first_name || member.user.username;
                        option.textContent = `${member.user.first_name || member.user.username} - ${member.specialization}`;
                        staffSelect.appendChild(option);
                    });
                    staffSelect.disabled = false;
                }
            } catch (error) {
                console.error('Error loading staff:', error);
                staffSelect.innerHTML = '<option value="">❌ Error loading staff</option>';
                staffSelect.disabled = true;
                
                // Show error message
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-danger mt-2';
                errorMsg.innerHTML = '<i class="fas fa-exclamation-circle"></i> Failed to load staff members. Please refresh the page or contact support.';
                staffSelect.parentElement.appendChild(errorMsg);
                setTimeout(() => errorMsg.remove(), 5000);
            } finally {
                staffLoader.style.display = 'none';
                staffSelect.style.display = 'block';
            }
        });
    }
    
    // Load schedules when staff is selected
    if (staffSelect) {
        staffSelect.addEventListener('change', async function() {
            const staffId = this.value;
            
            if (!staffId) {
                scheduleSelect.innerHTML = '<option value="">Select date & time</option>';
                scheduleSelect.disabled = true;
                selectedData.staff = null;
                updateSummary();
                updateSteps(2);
                submitBtn.disabled = true;
                return;
            }
            
            // Store selected staff data
            const selectedOption = this.options[this.selectedIndex];
            selectedData.staff = {
                id: staffId,
                name: selectedOption.dataset.name,
                specialization: selectedOption.dataset.specialization
            };
            
            updateSteps(3);
            updateSummary();
            
            // Show loader
            scheduleLoader.style.display = 'block';
            scheduleSelect.style.display = 'none';
            
            // Load available schedules
            try {
                const response = await fetch(`/api/schedules/?staff_id=${staffId}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const schedules = await response.json();
                
                scheduleSelect.innerHTML = '<option value="">Select your preferred time...</option>';
                
                if (schedules.length === 0) {
                    scheduleSelect.innerHTML = '<option value="">⚠️ No available time slots</option>';
                    scheduleSelect.disabled = true;
                    
                    // Show helpful message
                    const helpMsg = document.createElement('div');
                    helpMsg.className = 'alert alert-warning mt-2';
                    helpMsg.innerHTML = '<i class="fas fa-calendar-times"></i> This staff member has no available time slots. Please try another staff member or contact the salon.';
                    scheduleSelect.parentElement.appendChild(helpMsg);
                    setTimeout(() => helpMsg.remove(), 7000);
                } else {
                    schedules.forEach(schedule => {
                        const option = document.createElement('option');
                        option.value = schedule.id;
                        option.dataset.date = schedule.date;
                        option.dataset.time = schedule.time_slot;
                        
                        // Format date nicely
                        const dateObj = new Date(schedule.date + 'T00:00:00');
                        const dateStr = dateObj.toLocaleDateString('en-US', { 
                            weekday: 'short', 
                            month: 'short', 
                            day: 'numeric' 
                        });
                        
                        option.textContent = `${dateStr} at ${schedule.time_slot}`;
                        scheduleSelect.appendChild(option);
                    });
                    scheduleSelect.disabled = false;
                }
            } catch (error) {
                console.error('Error loading schedules:', error);
                scheduleSelect.innerHTML = '<option value="">❌ Error loading time slots</option>';
                scheduleSelect.disabled = true;
                
                // Show error message
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-danger mt-2';
                errorMsg.innerHTML = '<i class="fas fa-exclamation-circle"></i> Failed to load available time slots. Please refresh the page or contact support.';
                scheduleSelect.parentElement.appendChild(errorMsg);
                setTimeout(() => errorMsg.remove(), 7000);
            } finally {
                scheduleLoader.style.display = 'none';
                scheduleSelect.style.display = 'block';
            }
        });
    }
    
    // Update when schedule is selected
    if (scheduleSelect) {
        scheduleSelect.addEventListener('change', function() {
            const scheduleId = this.value;
            
            if (!scheduleId) {
                selectedData.schedule = null;
                updateSteps(3);
                submitBtn.disabled = true;
                updateSummary();
                return;
            }
            
            const selectedOption = this.options[this.selectedIndex];
            selectedData.schedule = {
                id: scheduleId,
                date: selectedOption.dataset.date,
                time: selectedOption.dataset.time
            };
            
            updateSteps(4);
            submitBtn.disabled = false;
            updateSummary();
        });
    }
    
    // Update booking summary
    function updateSummary() {
        if (!selectedData.service) {
            bookingSummary.innerHTML = `
                <div class="summary-empty">
                    <i class="fas fa-clipboard-check summary-icon"></i>
                    <p>Your booking details will appear here</p>
                    <small>Start by selecting a service</small>
                </div>
            `;
            return;
        }
        
        let summaryHTML = `
            <div class="summary-section">
                <div class="summary-item">
                    <div class="summary-icon-wrapper service-icon">
                        <i class="fas fa-scissors"></i>
                    </div>
                    <div class="summary-content">
                        <label>Service</label>
                        <strong>${selectedData.service.name}</strong>
                    </div>
                </div>
            </div>
            
            <div class="summary-section">
                <div class="summary-detail">
                    <i class="fas fa-dollar-sign"></i>
                    <span>Price: <strong>$${selectedData.service.price}</strong></span>
                </div>
                <div class="summary-detail">
                    <i class="fas fa-hourglass-half"></i>
                    <span>Duration: <strong>${selectedData.service.duration} mins</strong></span>
                </div>
            </div>
        `;
        
        if (selectedData.staff) {
            summaryHTML += `
                <div class="summary-section">
                    <div class="summary-item">
                        <div class="summary-icon-wrapper staff-icon">
                            <i class="fas fa-user-tie"></i>
                        </div>
                        <div class="summary-content">
                            <label>Staff Member</label>
                            <strong>${selectedData.staff.name}</strong>
                            <small>${selectedData.staff.specialization}</small>
                        </div>
                    </div>
                </div>
            `;
        }
        
        if (selectedData.schedule) {
            summaryHTML += `
                <div class="summary-section">
                    <div class="summary-item">
                        <div class="summary-icon-wrapper schedule-icon">
                            <i class="fas fa-calendar-alt"></i>
                        </div>
                        <div class="summary-content">
                            <label>Appointment</label>
                            <strong>${selectedData.schedule.date}</strong>
                            <small>${selectedData.schedule.time}</small>
                        </div>
                    </div>
                </div>
                
                <div class="summary-footer">
                    <div class="summary-total">
                        <span>Total Amount</span>
                        <strong>$${selectedData.service.price}</strong>
                    </div>
                </div>
            `;
        }
        
        bookingSummary.innerHTML = summaryHTML;
    }
    
    // Form validation
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            if (!serviceSelect.value || !staffSelect.value || !scheduleSelect.value) {
                e.preventDefault();
                alert('⚠️ Please complete all required fields before booking!');
                return false;
            }
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitBtn.disabled = true;
        });
    }
    
    // Auto-fill service from URL parameter if present (must be after event listeners are attached)
    const serviceIdFromURL = getURLParameter('service');
    if (serviceIdFromURL && serviceSelect) {
        // Set the service dropdown value
        serviceSelect.value = serviceIdFromURL;
        
        // Trigger the change event to load staff automatically
        if (serviceSelect.value === serviceIdFromURL) {
            // Successfully set the value, now trigger change event
            const event = new Event('change', { bubbles: true });
            serviceSelect.dispatchEvent(event);
        }
    }
});
