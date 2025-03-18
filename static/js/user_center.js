/*
#退出登录
document.getElementById('logout').addEventListener('click', logout);
#提交反馈和反馈相关
document.getElementById('feedback-btn').addEventListener('click', showFeedbackForm);
document.querySelector('.close-btn').addEventListener('click', hideFeedbackForm);
document.getElementById('submit-feedback').addEventListener('click', submitFeedback);

function logout() {
    alert("已退出登录！");
    session.pop('username', None)
    session.pop('userid', None)
    window.location.href = "/";
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
 */
// 打开支付弹窗
function openPaymentPopup() {
    document.getElementById("payment-popup").style.display = "block";
}

// 关闭支付弹窗
function closePaymentPopup() {
    document.getElementById("payment-popup").style.display = "none";
}

// 确认支付
function confirmPayment() {
    let duration = document.getElementById("membership-duration").value;  // 获取选择的会员期限

    fetch('/register_member', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ duration: duration })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert("会员注册成功！");
            closePaymentPopup();
            location.reload(); // 刷新页面
        } else {
            alert("注册失败：" + data.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("请求失败，请稍后再试！");
    });
}

