//直接查询老师名字
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

// 初始化当前页和每页显示的导师数量
let currentPage = 1;
const tutorsPerPage = 5;

// 监听表单提交，发送请求获取导师推荐
document.getElementById('recommendForm').addEventListener('submit', function (e) {
    e.preventDefault();  // 阻止表单默认提交

    let formData = {
        school: document.getElementById('school').value,
        graduationSchool: document.getElementById('graduationSchool').value,
        title: document.getElementById('title').value,
        major: document.getElementById('major').value,
        field: document.getElementById('field').value,
        otherRequirements: document.getElementById('otherRequirements').value,
        page: currentPage,
        per_page: tutorsPerPage
    };

    // 发送 AJAX 请求
    fetch('/get_recommended_tutors', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.length === 0) {
            document.getElementById('tutorCards').innerHTML = '<p>无符合条件的导师</p>';
            document.getElementById('pagination').style.display = 'none';  // 隐藏翻页按钮
        } else {
            displayTutors(data);
            updatePagination(data.length);
            document.getElementById('pagination').style.display = 'block';  // 显示翻页按钮
        }
    });
});

// 显示导师信息
function displayTutors(tutors) {
    let html = '';
    tutors.forEach(function (tutor) {
        html += `
            <div class="tutor-card" onclick="goToTeacherInfo('${tutor.Name}')">
                <h3>${tutor.Name}</h3>
                <p>学校: ${tutor.School}</p>
                <p>职称: ${tutor.Title}</p>
                <p>专业: ${tutor.Major}</p>
                <p>领域: ${tutor.Field}</p>
            </div>
        `;
    });
    document.getElementById('tutorCards').innerHTML = html;
}

// 更新翻页按钮
function updatePagination(totalTutors) {
    const totalPages = Math.ceil(totalTutors / tutorsPerPage);
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages;
}

// 翻页功能
document.getElementById('prevPage').addEventListener('click', function () {
    if (currentPage > 1) {
        currentPage--;
        document.getElementById('recommendForm').submit();
    }
});

document.getElementById('nextPage').addEventListener('click', function () {
    currentPage++;
    document.getElementById('recommendForm').submit();
});

// 跳转到教师详细信息页面
function goToTeacherInfo(name) {
    // 根据教师名字调用 search 函数并跳转
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: name })
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirectUrl) {
            window.location.href = data.redirectUrl;
        } else {
            alert('未找到该导师的信息');
        }
    });
}
