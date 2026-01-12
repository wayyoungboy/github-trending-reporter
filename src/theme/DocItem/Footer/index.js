import React from 'react';
import Footer from '@theme-original/DocItem/Footer';
import ReportActions from '@site/src/components/ReportActions';

export default function FooterWrapper(props) {
  return (
    <>
      <Footer {...props} />
      <ReportActions />
    </>
  );
}
