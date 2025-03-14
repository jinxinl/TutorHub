document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('search-button');
    const searchBox = document.getElementById('search-box');

    searchButton.addEventListener('click', function() {
        const searchContent = searchBox.value;

        // 发送搜索内容到后台
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: searchContent })
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirectUrl) {
                // 跳转到老师信息界面
                window.location.href = data.redirectUrl;
            } else {
                alert('未找到相关信息');
            }
        })
        .catch(error => {
            console.error('搜索请求失败:', error);
            alert('搜索请求失败，请重试');
        });
    });
});