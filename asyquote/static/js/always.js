function fadeOutAlerts() {
    var alerts = document.querySelectorAll('.alert-dismissible.alert-success');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.style.display = 'none';
            }, 500);
        }, 3000);
    });
}

fadeOutAlerts();
setInterval(fadeOutAlerts, 2000);

function fadeOutAlerts2() {
    var alerts2 = document.querySelectorAll('.alert-dismissible.alert-danger');
    alerts2.forEach(function (alert2) {
        setTimeout(function () {
            alert2.style.opacity = '0';
            setTimeout(function () {
                alert2.style.display = 'none';
            }, 500);
        }, 3000);
    });
}

fadeOutAlerts2();
setInterval(fadeOutAlerts2, 2000);

function fadeOutAlerts3() {
    var alerts3 = document.querySelectorAll('.alert-dismissible.alert-info');
    alerts3.forEach(function (alert3) {
        setTimeout(function () {
            alert3.style.opacity = '0';
            setTimeout(function () {
                alert3.style.display = 'none';
            }, 500);
        }, 3000);
    });
}

fadeOutAlerts3();
setInterval(fadeOutAlerts3, 2000);

function fadeOutAlerts4() {
    var alerts4 = document.querySelectorAll('.alert-dismissible.alert-error');
    alerts4.forEach(function (alert4) {
        setTimeout(function () {
            alert4.style.opacity = '0';
            setTimeout(function () {
                alert4.style.display = 'none';
            }, 500);
        }, 3000);
    });
}

fadeOutAlerts4();
setInterval(fadeOutAlerts4, 2000);

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.querySelector('.image-file-uploader');
    const fileLabel = document.querySelector('.custom-file-label');
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const fileName = e.target.files[0].name;
            const maxLength = 50;
            if (fileName.length > maxLength) {
                fileLabel.textContent = fileName.substring(0, maxLength) + '...';
            } else {
                fileLabel.textContent = fileName;
            }
        });
    }

});
