export const commonChartTheme = {
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif",
    color: '#94a3b8',
  },
  grid: {
    top: 36,
    right: 16,
    bottom: 30,
    left: 48,
    containLabel: false,
  },
  tooltip: {
    trigger: 'axis' as const,
    backgroundColor: '#0c1527',
    borderColor: 'rgba(15, 202, 240, 0.4)',
    borderWidth: 1,
    padding: [8, 12],
    textStyle: {
      color: '#ffffff',
      fontSize: 12,
    },
    axisPointer: {
      type: 'cross' as const,
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.2)',
        type: 'dashed' as const,
      },
      crossStyle: {
        color: 'rgba(255, 255, 255, 0.2)',
      },
    },
  },
  legend: {
    top: 4,
    right: 16,
    textStyle: {
      color: '#cbd5e1',
      fontSize: 12,
    },
    itemWidth: 12,
    itemHeight: 8,
    borderRadius: 2,
  },
}

export const axisStyle = {
  axisLine: {
    show: true,
    lineStyle: {
      color: 'rgba(255, 255, 255, 0.1)',
    },
  },
  axisTick: {
    show: false,
  },
  axisLabel: {
    color: '#94a3b8',
    fontSize: 11,
  },
  splitLine: {
    show: true,
    lineStyle: {
      color: 'rgba(255, 255, 255, 0.06)',
      type: 'dashed' as const,
    },
  },
}
