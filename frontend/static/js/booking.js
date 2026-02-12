// Booking Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const serviceSelect = document.getElementById('service_id');
    const staffSelect = document.getElementById('staff_id');
    const scheduleSelect = document.getElementById('schedule_id');
    const bookingSummary = document.getElementById('booking-summary');
    
    // Load staff when service is selected
    if (serviceSelect) {
        serviceSelect.addEventListener('change', async function() {
            const serviceId = this.value;
            
            if (!serviceId) {
                staffSelect.innerHTML = '<option value="">Select staff</option>';
                scheduleSelect.innerHTML = '<option value="">Select date & time</option>';
                updateSummary();
                return;
            }
            
            // Update summary
            updateSummary();
            
            // Load staff for selected service
            try {
                const response = await fetch(`/api/staff/?service_id=${serviceId}`);
                const staff = await response.json();
                
                staffSelect.innerHTML = '<option value="">Select staff</option>';
                staff.forEach(member => {
                    const option = document.createElement('option');
                    option.value = member.id;
                    option.textContent = `${member.user.first_name || member.user.username} - ${member.specialization}`;
                    staffSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading staff:', error);
            }
        });
    }
    
    // Load schedules when staff is selected
    if (staffSelect) {
        staffSelect.addEventListener('change', async function() {
            const staffId = this.value;
            
            if (!staffId) {
                scheduleSelect.innerHTML = '<option value="">Select date & time</option>';
                return;
            }
            
            // Load available schedules
            try {
                const response = await fetch(`/api/schedules/?staff_id=${staffId}`);
                const schedules = await response.json();
                
                scheduleSelect.innerHTML = '<option value="">Select date & time</option>';
                schedules.forEach(schedule => {
                    const option = document.createElement('option');
                    option.value = schedule.id;
                    option.textContent = `${schedule.date} - ${schedule.time_slot}`;
                    scheduleSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading schedules:', error);
            }
        });
    }
    
    // Update booking summary
    function updateSummary() {
        const selectedService = serviceSelect.options[serviceSelect.selectedIndex];
        
        if (!selectedService || !selectedService.value) {
            bookingSummary.innerHTML = '<p class="text-muted">Select a service to see details</p>';
            return;
        }
        
        const serviceName = selectedService.textContent.split(' - ')[0];
        const price = selectedService.dataset.price;
        const duration = selectedService.dataset.duration;
        
        bookingSummary.innerHTML = `
            <div class="mb-3">
                <h5>${serviceName}</h5>
                <p class="mb-2"><strong>Price:</strong> $${price}</p>
                <p class="mb-2"><strong>Duration:</strong> ${duration} minutes</p>
            </div>
        `;
    }
    
    // Form validation
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            if (!serviceSelect.value || !staffSelect.value || !scheduleSelect.value) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    }
});
