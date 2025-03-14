document.getElementById('logout').addEventListener('click', logout);
document.getElementById('feedback-btn').addEventListener('click', showFeedbackForm);
document.querySelector('.close-btn').addEventListener('click', hideFeedbackForm);
document.getElementById('submit-feedback').addEventListener('click', submitFeedback);

function logout() {
    alert("已退出登录！");
    window.location.href = "/login";
}

function showFeedbackForm() {
    document.getElementById('feedback-form').style.display = 'block';
}

function hideFeedbackForm() {
    document.getElementById('feedback-form').style.display = 'none';
}

function submitFeedback() {
    var feedbackText = document.getElementById('feedback-text').value;
    if (feedbackText.trim() === '') {
        alert("反馈内容不能为空!");
        return;
    }

    // 发送反馈数据到服务器
    fetch('/submit_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ feedback: feedbackText })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("反馈提交成功!");
            hideFeedbackForm();
            document.getElementById('feedback-text').value = '';
        } else {
            alert("反馈提交失败，请重试!");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("反馈提交失败，请重试!");
    });
}