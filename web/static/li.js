/**
 * Created by liwang on 2/17/16.
 *
 * require d3.js*/
var list_reduce = function (list, func, compute_func) {
    return list.reduce(function (a, b) {
        return func(a, b, compute_func) ? a : b;
    });
}
var larger_than = function (a, b, compute_func) {
    return compute_func(a) > compute_func(b);
}
var smaller_than = function (a, b, compute_func) {
    return compute_func(a) < compute_func(b);
}

var distance = function (v1, v2, keys) {
    var dis = 0.0;
    for (var k in keys) {
        dis += Math.pow(parseFloat(v1[keys[k]]) - parseFloat(v2[keys[k]]), 2);
    }
    return dis;
}
var distance_sqrt = function (v1, v2, keys) {
    return Math.sqrt(distance(v1, v2, keys));
}

function deepcopy(list, keys) {
    var a = [];
    for (var i in list) {
        var b = {};
        keys.forEach(function (k) {
            b[k] = list[i][k];
        });
        a.push(b);
    }
    return a;
}

function randomdataset(k, p, width, padding, radius) {
    var count = 0;
    var result = [];
    var w = 0;
    var randomclustercount = [];
    while (w++ < k) {
        randomclustercount.push({
            d0: Math.random() * width * (1 - 2 * padding) + width * padding,
            d1: Math.random() * width * (1 - 2 * padding) + width * padding
        });
    }
    while (count++ < p) {
        var rindex = Math.round(Math.random() * 1000) % k;
        var positive0 = Math.round(Math.random() * 1000) % 2 == 1;
        var positive1 = Math.round(Math.random() * 1000) % 2 == 1;
        var r01 = Math.random();
        var r02 = Math.random();
        var r11 = Math.random();
        var r12 = Math.random();
        result.push({
            index: count,
            d0: randomclustercount[rindex].d0 + (positive0
                ? (r01 * width * radius) : (0 - r02 * width * radius)),
            d1: randomclustercount[rindex].d1 + (positive1
                ? (r11 * width * radius) : (0 - r12 * width * radius))
        });
    }
    return result;
}