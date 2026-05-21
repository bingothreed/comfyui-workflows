按 F12（或 Ctrl+Shift+I），点击顶部的 Console（控制台） 标签。

方案A：只获取节点列表（轻量，推荐先跑这个）

```
(async function() {
    'use strict';
    const iframe = document.querySelector('iframe');
    if (!iframe || !iframe.contentWindow) {
        alert('❌ 无法访问ComfyUI iframe，请确认页面已完全加载');
        return;
    }
    const iframeWindow = iframe.contentWindow;
    let allNodes = {};
    let nodeCount = 0;
    if (iframeWindow.LiteGraph && iframeWindow.LiteGraph.registered_node_types) {
        const liteGraphNodes = iframeWindow.LiteGraph.registered_node_types;
        console.log('✅ 找到节点:', Object.keys(liteGraphNodes).length);
        Object.entries(liteGraphNodes).forEach(([nodeName, nodeClass]) => {
            allNodes[nodeName] = {
                name: nodeName,
                category: nodeClass.category || 'unknown',
                title: nodeClass.title || nodeName,
                description: nodeClass.desc || '',
            };
            nodeCount++;
        });
    } else {
        alert('❌ 未找到 LiteGraph，请等待页面完全加载后重试');
        return;
    }
    const categories = {};
    Object.values(allNodes).forEach(node => {
        const cat = node.category || 'unknown';
        categories[cat] = (categories[cat] || 0) + 1;
    });
    const report = {
        summary: { total_nodes: nodeCount, categories_count: Object.keys(categories).length, extraction_timestamp: new Date().toISOString() },
        categories: categories,
        nodes: allNodes
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `runninghub_nodes_list_${nodeCount}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    console.log(`✅ 完成！共 ${nodeCount} 个节点，文件已下载`);
    return report.summary;
})();
```

方案B：获取完整参数（22MB，内容最全）

```
(async function() {
    'use strict';
    console.log('🌐 请求 /object_info...');
    try {
        const response = await fetch('/object_info');
        if (!response.ok) throw new Error(`请求失败: ${response.status}`);
        const nodeData = await response.json();
        const nodeCount = Object.keys(nodeData).length;
        console.log(`✅ 成功获取 ${nodeCount} 个节点`);
        const blob = new Blob([JSON.stringify(nodeData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `runninghub_COMPLETE_PARAMS_${nodeCount}_nodes.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        alert(`🎉 完成！${nodeCount} 个节点，文件已下载！`);
    } catch (error) {
        alert(`❌ 失败: ${error.message}`);
    }
})();
```

