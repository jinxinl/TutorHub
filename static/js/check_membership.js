function checkMembership() {
    // 使用全局变量 tname
    var tname = window.tname;

    // 发送 AJAX 请求到 /check_membership，并传递 tname 参数
    fetch('/check_membership?tname=' + encodeURIComponent(tname))
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.show_graphs) {
                // 显示图表容器
                document.getElementById('graphs-container').style.display = 'block';

                // 更新图像的 src 属性
                document.getElementById('alumni-graph').src = 'data:image/png;base64,' + data.alumni_graph;
                document.getElementById('tutor-rel-graph').src = 'data:image/png;base64,' + data.tutor_rel_graph;
            } else if (data.status === 'error') {
                alert(data.message);
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    window.history.back();
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}