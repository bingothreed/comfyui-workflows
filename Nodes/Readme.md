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

方案B：获取完整参数（内容最全，含 input/output schema）

注意：runninghub 的 `/object_info` 返回的是包装格式 `{ nodes_info: {...}, checkpoints: [], loras: [] }`，
节点字典在 `nodes_info` 字段里，不是顶层。直接 `Object.keys(nodeData).length` 只会得到 3。

```
(async function() {
    'use strict';
    console.log('🌐 请求 /object_info...');
    try {
        const response = await fetch('/object_info');
        if (!response.ok) throw new Error(`请求失败: ${response.status}`);
        const nodeData = await response.json();

        // runninghub 把节点字典放在 nodes_info 里；原生 ComfyUI 则节点直接在顶层。两种都兼容。
        const nodesDict = nodeData.nodes_info && typeof nodeData.nodes_info === 'object'
            ? nodeData.nodes_info
            : nodeData;
        const nodeCount = Object.keys(nodesDict).length;
        console.log(`✅ 成功获取 ${nodeCount} 个节点`);
        if (nodeData.checkpoints || nodeData.loras) {
            console.log(`   附带 checkpoints: ${(nodeData.checkpoints || []).length}, loras: ${(nodeData.loras || []).length}`);
        }
        if (nodeCount < 100) {
            console.warn(`⚠️ 节点数仅 ${nodeCount}，可能页面没加载完，建议刷新后重试`);
        }

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

### 之前 `_3_nodes.json` 文件名的由来

旧脚本里 `Object.keys(nodeData).length` 数的是顶层 key 数量，runninghub 返回 `{nodes_info, checkpoints, loras}` 三个字段，所以文件名被命成了 `_3_nodes`。
**但文件内容是完整的**，里面 `nodes_info` 字段下有 14000+ 个节点，可以直接用。新脚本已修复这个统计 bug。

